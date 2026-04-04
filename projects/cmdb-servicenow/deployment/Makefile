# CMDB ServiceNow Discovery - Makefile

.PHONY: help build test run deploy clean install

# Configuration
IMAGE_NAME = cmdb-discovery
IMAGE_TAG ?= latest
REGISTRY ?= registry.internal.com
NAMESPACE ?= ti-operations

# Paths
PROJECT_DIR := $(shell pwd)
IMPLEMENTATION_DIR = $(PROJECT_DIR)/implementation

help:
	@echo "CMDB Discovery - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  build          Build Docker image"
	@echo "  push           Push Docker image to registry"
	@echo "  test           Run tests"
	@echo "  test-cov       Run tests with coverage"
	@echo "  run            Run discovery locally"
	@echo "  deploy         Deploy to Kubernetes"
	@echo "  deploy-cron    Deploy CronJob to Kubernetes"
	@echo "  clean          Clean up"
	@echo "  install        Install dependencies"

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(PROJECT_DIR)/deployment/Dockerfile $(PROJECT_DIR)

push:
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
	docker push $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

test:
	cd $(IMPLEMENTATION_DIR) && pip3 install -q -r requirements.txt
	cd $(PROJECT_DIR)/tests && pytest -v

test-cov:
	cd $(PROJECT_DIR)/tests && pytest --cov=implementation --cov-report=html --cov-report=term

run:
	cd $(IMPLEMENTATION_DIR) && \
	CONFIG_PATH=$(PROJECT_DIR)/config/config.yaml \
	python3 main.py

deploy:
	kubectl apply -f $(PROJECT_DIR)/deployment/k8s/

deploy-cron:
	kubectl apply -f $(PROJECT_DIR)/deployment/k8s/cronjob.yaml

clean:
	rm -rf $(PROJECT_DIR)/tests/__pycache__
	rm -rf $(IMPLEMENTATION_DIR)/**/__pycache__
	rm -rf $(PROJECT_DIR)/tests/.coverage
	rm -rf $(PROJECT_DIR)/tests/htmlcov
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG) 2>/dev/null || true

install:
	cd $(IMPLEMENTATION_DIR) && pip3 install -r requirements.txt

validate-config:
	bash $(PROJECT_DIR)/scripts/validate-config.sh

health-check:
	bash $(PROJECT_DIR)/scripts/health-check.sh