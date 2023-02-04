PWD = $(shell pwd)
whoami = $(shell whoami)
VERSION = 1.4.1
VERBOSE ?= 

# ------------------------------------------------------------------
# Set up path local clone of dependencies supercede the installed ones.

SRC_PATH=$(PWD)/src
BASIC_PATH=/22/dls-utilpack/src:/22/dls-normsql/src:/22/dls-siggy/src:/22/dls-logformatter/src
BILLY_PATH=/22/dls-servbase/src
MAINIAC_PATH=/22/dls-mainiac/src
VALKYRIE_PATH=/22/dls-pairstream/src
PYTHONPATH=$(SRC_PATH):$(BASIC_PATH):$(BILLY_PATH):$(MAINIAC_PATH):$(VALKYRIE_PATH)

# ------------------------------------------------------------------
# Tests.

pytest:
	PYTHONPATH=$(PYTHONPATH) \
	ISPYB_CREDENTIALS=$(ISPYB_LOCAL_CREDENTIALS) \
	python3 -m pytest

test:
	PYTHONPATH=tests:$(PYTHONPATH) \
	python3 -m pytest -sv -ra --tb=line tests/$(t)
	
# ------------------------------------------------------------------

link_data:
	mkdir -p /dls/science/groups/i04-1/software/luigi_pipeline
	ln -s /27/datasets/xchem/imager_pipe /dls/science/groups/i04-1/software/luigi_pipeline


service ?= dls_servbase_dataface dataface collector gui

start:
	PYTHONPATH=$(PYTHONPATH) \
	ECHOLOCATOR_CONFIGFILE=configurations/development.yaml \
	python3 -m echolocator_cli.main start_services $(service) \
	$(V)

# ------------------------------------------------------------------
# Deployment for runtime.
# A "module load echolocator/{version}/conda" will activate a conda environment.
# A "module load echolocator/{version}/paths" will set the PYTHONPATH to reach this deployment.
# Instead of {version}, you can use "edge" to get the lastest version.
MODULE_TARGET ?= /dls_sw/apps/Modules/modulefiles/xchem/echolocator
deploy_modules:
	mkdir -p $(MODULE_TARGET)/$(VERSION)
	cp modulefiles/* $(MODULE_TARGET)/$(VERSION)
	rm -f $(MODULE_TARGET)/edge
	ln -s $(MODULE_TARGET)/$(VERSION) $(MODULE_TARGET)/edge
	find $(MODULE_TARGET) -type f -exec chmod 664 {} \;
	find $(MODULE_TARGET) -type d -exec chmod g+s {} \;
	chgrp -R dls-softinst $(MODULE_TARGET)
	

# ---------------------------------------------------------------------------
# Building conda. 
CONDA_PREFIX = /dls_sw/apps/xchem/conda/envs/echolocator/$(VERSION)
PYTHON_VERSION = 3.9

create_conda_environment:
	mkdir -p /dls_sw/apps/xchem/conda
	chgrp dls-softinst /dls_sw/apps/xchem/conda
	chmod g+s /dls_sw/apps/xchem/conda
	module load mamba && \
	mamba create -y --prefix $(CONDA_PREFIX) python=$(PYTHON_VERSION)

install_conda_requirements:
	module load mamba && \
	mamba install -y --file conda-recipe/conda_requirements.txt --prefix $(CONDA_PREFIX)

install_conda_packages:
	module load mamba && \
	make _install_dependencies PIP_TARGET=$(CONDA_PREFIX)/lib/python3.9/site-packages

build_conda_environment:
	make create_conda_environment
	make install_conda_requirements
	make install_conda_packages
	make deploy_pippy_packages
	@echo "conda environment has been built in $(CONDA_PREFIX)"

# ------------------------------------------------------------------
# Install into pip on the shared filesystem (without conda).

PIPPY_PREFIX = /dls_sw/apps/xchem/pippy_place/echolocator/$(VERSION)

deploy_pippy_packages:
	mkdir -p /dls_sw/apps/xchem/pippy_place
	chgrp dls-softinst /dls_sw/apps/xchem/pippy_place
	chmod g+s /dls_sw/apps/xchem/pippy_place
	module load mamba && \
	make _install_dependencies PIP_TARGET=$(PIPPY_PREFIX)


# ------------------------------------------------------------------
# Install dependencies from pip.

_install_dependencies:
	pip install --no-deps --python-version $(PYTHON_VERSION) --target $(PIP_TARGET) --upgrade . && rm -rf build
	pip install --no-deps --python-version $(PYTHON_VERSION) --target $(PIP_TARGET) --upgrade git+https://gitlab.diamond.ac.uk/scisoft/dls-servbase.git && rm -rf build
	pip install --no-deps --python-version $(PYTHON_VERSION) --target $(PIP_TARGET) --upgrade git+https://gitlab.diamond.ac.uk/scisoft/bxflow/dls-mainiac.git && rm -rf build
	pip install --no-deps --python-version $(PYTHON_VERSION) --target $(PIP_TARGET) --upgrade git+https://gitlab.diamond.ac.uk/scisoft/bxflow/dls-siggy.git && rm -rf build
	pip install --no-deps --python-version $(PYTHON_VERSION) --target $(PIP_TARGET) --upgrade git+https://gitlab.diamond.ac.uk/scisoft/bxflow/dls-pairstream.git && rm -rf build
	pip install --no-deps --python-version $(PYTHON_VERSION) --target $(PIP_TARGET) --upgrade git+https://gitlab.diamond.ac.uk/scisoft/dls-utilpack.git && rm -rf build
	pip install --no-deps --python-version $(PYTHON_VERSION) --target $(PIP_TARGET) --upgrade git+https://gitlab.diamond.ac.uk/scisoft/bxflow/dls-logformatter.git && rm -rf build
	pip install --no-deps --python-version $(PYTHON_VERSION) --target $(PIP_TARGET) --upgrade git+https://gitlab.diamond.ac.uk/scisoft/dls-normsql.git && rm -rf build

# ------------------------------------------------------------------
# Example data.
EXAMPLE_IMAGES_TARGET = /dls_sw/apps/xchem/example_data/echolocator/example_images
deploy_example_data:
	rsync -a tests/example_images/* $(EXAMPLE_IMAGES_TARGET)
	chgrp -R dls-softinst $(EXAMPLE_IMAGES_TARGET)
	find $(EXAMPLE_IMAGES_TARGET) -type d -exec chmod g+s {} \;

	
# ------------------------------------------------------------------
# Documentation.
# (in docker)  make build_sphinx
# (in windows) make rsync
# (in linux)   make publish_docs

build_docs:
	mkdir -p public
	PYTHONPATH=$(PYTHONPATH) \
	sphinx-build -EWT --keep-going docs public
	touch build/html/.nojekyll
 
# These locations are patterned after this file:
# https://gitlab.diamond.ac.uk/controls/reports/ci_templates/-/blob/master/defaults.yml
DOCS_PUBLISH_ROOT = /dls/cs-www/reports/gitlab-ci/echolocator/docs
DOCS_PUBLISH_URL = http://www.cs.diamond.ac.uk/reports/gitlab-ci/echolocator/docs
publish_docs:
	mkdir -p $(DOCS_PUBLISH_ROOT)/$(VERSION)
	cp -rf public/* $(DOCS_PUBLISH_ROOT)/$(VERSION)
	rm -f $(DOCS_PUBLISH_ROOT)/latest
	ln -s $(VERSION) $(DOCS_PUBLISH_ROOT)/latest
	@echo "Documentation is available at $(DOCS_PUBLISH_URL)/latest"

# ------------------------------------------------------------------
# Rsync stuff from local C: drive to shared V: drive. 

rsync:	
	../kbp43231_scripts/myrsync.py echolocator
	
# ------------------------------------------------------------------
# Utility.

.PHONY: list
list:
	@awk "/^[^\t:]+[:]/" Makefile | grep -v ".PHONY"

clean:
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '__pycache__' -exec rm -rf {} \;

show_version:
	PYTHONPATH=$(PYTHONPATH) python3 src/echolocator_lib/version.py --json
	PYTHONPATH=$(PYTHONPATH) python3 src/echolocator_lib/version.py

# ------------------------------------------------------------------
# Version bumping.  Configured in setup.cfg. 
# Thanks: https://pypi.org/project/bump2version/
bump-patch:
	bump2version --list patch

bump-minor:
	bump2version --list minor

bump-major:
	bump2version --list major
	
bump-dryrun:
	bump2version --dry-run patch

# Saved 44

