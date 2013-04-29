#!/bin/bash 

DOMAIN="plone.contentratings"

# If you want to add another language create folders and empty file:
#   mkdir -p locales/<lang_code>/LC_MESSAGES
#   touch locales/<lang_code>/LC_MESSAGES/$DOMAIN.po
# and run this script
# Example: locales/hu/LC_MESSAGES/$DOMAIN.po

touch locales/$DOMAIN.pot
i18ndude rebuild-pot --pot locales/$DOMAIN.pot --create $DOMAIN ./
i18ndude merge --pot locales/${DOMAIN}.pot --merge locales/${DOMAIN}-manual.pot


# sync all locales
find locales -type d -depth 1 \
     | grep -v .svn \
     | sed -e "s/locales\/\(.*\)$/\1/" \
     | xargs -I % i18ndude sync --pot locales/$DOMAIN.pot locales/%/LC_MESSAGES/$DOMAIN.po
