DATE = "date"
DATE_TIME = "datetime"
DATE_TIME_LOCAL = "datetim-local"
EMAIL = "email"
FILE = "file"
HIDDEN = "hidden"
MONTH = "month"
NUMBER = "number"
PASSWORD = "password"
TEXT = "text"
TEXT_AREA = "textarea"

def as_list():

	return [
		DATE,
		DATE_TIME,
		DATE_TIME_LOCAL,
		EMAIL,
		FILE,
		HIDDEN,
		MONTH,
		NUMBER,
		PASSWORD,
		TEXT,
		TEXT_AREA,
	]

#  Leaving out minlength for now from list so it's not implemented in all browsers



COMMON_ATTRS = [
	"autocomplete",
	"autofocus",
	"disabled",
	"maxlength",
	"pattern",
	"placeholder",
	"readonly",
	"required",
	#"value",
	]

NUM_ATTRS = COMMON_ATTRS + [
	"min",
	"max",
]

FILE_ATTRS = [
	"accept",

	"disabled",
	"required",
]

TEXT_AREA_ATTRS = [
	"autofocus",
	"cols",
	"disabled",
	"maxlength",
	"placeholder"
	"readonly",
	"required",
	"rows",
	"value",
]

ATTRS = {

	DATE: NUM_ATTRS,
	DATE_TIME: NUM_ATTRS,
	DATE_TIME_LOCAL: NUM_ATTRS,
	EMAIL: COMMON_ATTRS,
	FILE: FILE_ATTRS,
	HIDDEN: COMMON_ATTRS,
	MONTH: NUM_ATTRS,
	PASSWORD: COMMON_ATTRS,
	TEXT: COMMON_ATTRS,
}

