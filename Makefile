.PHONY: prepare build check test release clean-source

prepare:
	python3 scripts/prepare.py

build:
	sh scripts/build.sh all

check:
	docker run --rm --user $$(id -u):$$(id -g) -v $(CURDIR)/build/source:/source:ro -v $(CURDIR)/build/work:/work banana-duolite-native-builder:bookworm python3 /source/tools/duolite/check-image.py --images /work/native/images --tools /work/native/host/bin

test: prepare
	python3 tests/test-update.py
	bash build/source/ui/tests/update-apply.sh
	python3 build/source/system/bananad/tests/test-duolite-hardware.py

release: build check test
	sh scripts/build.sh legal-info
	python3 scripts/package.py --images build/work/native/images --source build/source --legal build/work/native/legal-info --output dist

clean-source:
	python3 -c "import shutil; shutil.rmtree('build/source', ignore_errors=True); shutil.rmtree('build/source.new', ignore_errors=True)"
