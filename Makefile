.PHONY: recovery assets deploy training-submit training-registry monitor failure alert ci-setup ci-evidence delivery cold portability-audit cloud-check teardown

assets:
	python -m cloudlayer.finish assets

deploy:
	python -m cloudlayer.finish deploy

training-submit:
	python -m cloudlayer.finish training-submit

training-registry:
	python -m cloudlayer.finish training-registry

monitor:
	python -m cloudlayer.finish monitor

failure:
	python -m cloudlayer.finish failure

alert:
	python -m cloudlayer.finish alert

ci-setup:
	python -m cloudlayer.finish ci-setup

ci-evidence:
	python -m cloudlayer.finish ci-evidence

delivery:
	python -m cloudlayer.finish delivery

cold:
	python -m cloudlayer.finish cold

portability-audit:
	python scripts/portability_audit.py

cloud-check:
	python scripts/cloud_check.py

teardown:
	test -n "$(CONFIRM_GROUP)"
	python -m cloudlayer.cleanup --confirm-group "$(CONFIRM_GROUP)"

recovery:
	python -m cloudlayer.finish recovery
