#!/usr/bin/make -f

NAME = musicdb
SITE = musicdb.chris-lamb.co.uk
MACHINE = tomo.chris-lamb.co.uk

export PYTHONDONTWRITEBYTECODE = 1

all: test build deploy

test:
	/manage.py test --verbosity=2

build:
	$(NAME)/manage.py build live

deploy:
	rsync -e ssh -avz --delete --exclude-from .rsyncignore ./ jenkins@$(MACHINE):/srv/$(SITE)
	ssh jenkins@$(MACHINE) sudo make -C /srv/$(SITE) install

install:
	ln -sf $(CURDIR)/config/gunicorn /etc/gunicorn.d/$(NAME)
	invoke-rc.d gunicorn restart
	
	ln -sf $(CURDIR)/config/nginx /etc/nginx/sites-enabled/$(NAME)
	invoke-rc.d nginx restart
	
	$(NAME)/manage.py migrate --list
