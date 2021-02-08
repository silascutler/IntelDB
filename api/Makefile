IMAGEID = $(shell eval docker images -aq inteldb/api_v1.1 )
LOCAL_PKG_DIR := $(shell eval pwd)


build:
	docker build -t inteldb/api_v1.1 .

test:
	docker run inteldb/api_v1.1

buildtest:
	docker build -t inteldb/api_v1.1 .
	docker run inteldb/api_v1.1
