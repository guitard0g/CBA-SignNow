import os
import re

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


class InvalidArgumentError(Exception):
    """Raised when the argument value is invalid"""

    pass


class MissingArgumentError(Exception):
    """Raised when a required argument is missing"""

    pass


def enum(**enums):
    return type("Enum", (), enums)


class Tags(object):
    BASE_TAGS = {
        "type": "t",  # type
        "required": "r",  # required
        "role": "o",  # role
        "label": "l",  # label
        "dropdown": "dd",  # dropdown
        "file": "f",  # file
        "width": "w",  # width
        "height": "h",  # height
        "validator": "v",  # validator_id
    }

    TAG_ORDER = [
        "type",
        "required",
        "role",
        "label",
        "dropdown",
        "file",
        "width",
        "height",
        "validator",
    ]

    TAG_TYPES = {
        "signature": "s",
        "initials": "i",
        "text": "t",
        "dropdown": "d",
        "checkbox": "c",
    }

    DATA_VALIDATOR_DICT = dict(
        DD_MM_YYYY="059b068ef8ee5cc27e09ba79af58f9e805b7c2b3",
        DATE_AND_TIME="06448a0d0eb6a71c7c116ec4754bcb04ebf11da5",
        DD_MON_YYYY="07c1e60f3da1192b60aca6f7e72d9b17a44539e5",
        TIME_ONLY="09d3bb6a5eb6598edb7bfad02b0143d8c68ad788",
        DD_MM_YY="0b61eb6a696da953910f195b30c86e5131f3ae3e",
        MMM_DD_YYYY="0f4827a308018f98b11ae3923104685ff0c03070",
        DATE_ONLY="13435fa6c2a17f83177fcbb5c4a9376ce85befeb",
        NUMERIC="1109cfbbb06311a06a4c7f8d04f1f0d5c44103cb",
        US_PHONE_NUMBER="13cc1d661da456d27b249b73056ed4d1f2e72d8e",
        US_CURRENCY="150662c7221a6a6ebcbb7c50ca46359d19757f81",
        US_ZIP="1671f4eb87444a24e1e00f149bade8b7cf3af5da",
        AGE="1a203fa91791b0458608be045a454ba90557fb26",
        POSITIVE_INT="1f9486ae822d30ba3df2cb8e65303ebfb8c803e8",
        POS_NEG_INT="23a57c29fa089e22bcf85d601c8091bc9c7da570",
        US_STATE="3123849de563f9e14acacc2739467e3d30e426b6",
        ALPHANUMERIC="3859296fffd39cb8efeaffda5899973c014ce42e",
        EMAIL="7cd795fd64ce63b670b52b2e83457d59ac796a39",
    )

    DATA_VALIDATORS = enum(**DATA_VALIDATOR_DICT)

    @staticmethod
    def __type_validator(typ):
        if typ in Tags.TAG_TYPES:
            return Tags.TAG_TYPES[typ]
        raise InvalidArgumentError("invalid tag type")

    @staticmethod
    def __required_validator(required):
        if required:
            return "y"
        return "n"

    @staticmethod
    def __role_validator(role):
        return '"' + str(role) + '"'

    @staticmethod
    def __label_validator(label):
        return '"' + str(label) + '"'

    @staticmethod
    def __dropdown_validator(dropdown):
        dd_string = '"'
        for option in dropdown:
            if not isinstance(option, str):
                raise InvalidArgumentError("non-string dropdown option")
            else:
                dd_string = dd_string + str(option) + ","
        return dd_string[:-1] + '"'  # cut off the last comma

    @staticmethod
    def __file_validator(fil):
        if os.path.isfile(fil):
            return '"' + fil + '"'
        raise InvalidArgumentError("invalid file")

    @staticmethod
    def __dimension_validator(dim):
        try:
            return str(int(dim))
        except ValueError:
            raise InvalidArgumentError("invalid dimension")

    @staticmethod
    def __validator_validator(validator):
        if validator in list(Tags.DATA_VALIDATOR_DICT.values()):
            return '"' + validator + '"'
        raise InvalidArgumentError("invalid validator")

    @staticmethod
    def __run_validator(key, val):
        return {
            "type": Tags.__type_validator,
            "required": Tags.__required_validator,
            "role": Tags.__role_validator,
            "label": Tags.__label_validator,
            "dropdown": Tags.__dropdown_validator,
            "file": Tags.__file_validator,
            "width": Tags.__dimension_validator,
            "height": Tags.__dimension_validator,
            "validator": Tags.__validator_validator,
        }[key](val)

    @staticmethod
    def __validate_args(args):
        def validate(arg):
            key, val = arg
            return key, Tags.__run_validator(key, val)

        formatted_args = dict(list(map(validate, list(args.items()))))
        if "type" not in formatted_args:
            raise MissingArgumentError("type argument is required")
        if "role" not in formatted_args:
            raise MissingArgumentError("role argument is required")
        if "width" not in formatted_args:
            raise MissingArgumentError("width argument is required")
        if "height" not in formatted_args:
            raise MissingArgumentError("height argument is required")

        typ = formatted_args["type"]

        if "label" in formatted_args and typ != "t" and typ != "dd":
            formatted_args.pop("label")
        if "dropdown" in formatted_args and typ != "dd":
            formatted_args.pop("dropdown")
        if "validator" in formatted_args and typ != "t":
            formatted_args.pop("dropdown")

        return formatted_args

    @staticmethod
    def create(**kwargs):
        validated_args = Tags.__validate_args(kwargs)
        text_tag = ""
        for key in Tags.TAG_ORDER:
            if key in validated_args:
                abbr = Tags.BASE_TAGS[key]
                text_tag = text_tag + abbr + ":" + validated_args[key] + ";"
        return "{{" + text_tag + "}}"

    @staticmethod
    def create_email(role, email, order=1):
        if not EMAIL_REGEX.match(email):
            raise InvalidArgumentError("Invalid email address")
        text_tag = 't:e;o:"{role}";e:"{email}";order:{order};'
        return "{{" + text_tag.format(role=role, email=email, order=order) + "}}"
