IMAGE_NAME = stepic/video-compressor
IMAGE_TAG = $(shell date +%Y%m%d)$(if $(BUILD_NUMBER),.$(BUILD_NUMBER),)

docker-build:
	@date > build_date
	@docker build -t $(IMAGE_NAME) .
	@rm -f build_date
	@docker tag $(IMAGE_NAME) $(IMAGE_NAME):$(IMAGE_TAG)

docker-push:
	@docker push $(IMAGE_NAME)
