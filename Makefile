IMAGE_NAME = docker.io/stepic/video-compressor
IMAGE_TAG = $(shell date +%Y%m%d)$(if $(BUILD_NUMBER),.$(BUILD_NUMBER),)

docker-build:
	@docker build -t $(IMAGE_NAME) .
	@docker tag $(IMAGE_NAME) $(IMAGE_NAME):$(IMAGE_TAG)

docker-push:
	@echo "Y" | docker push $(IMAGE_NAME)
