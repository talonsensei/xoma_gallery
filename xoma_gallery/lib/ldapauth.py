from django.conf import settings
from django.contrib.auth.models import User

import logging
import pdb

class ActiveDirectorySSLBackend:
  from django.conf import settings
  from django.contrib.auth.models import User
  
  settings = dict.fromkeys(
      ('AD_LDAP_URL', 'AD_SEARCH_DN', 'AD_NT4_DOMAIN', 'AD_CERT_FILE', 'AD_CERT_PATH'))
  
  def __init__(self):
    # Load settings from settings.py, put them in self.settings
    for var in self.settings.iterkeys():
      if hasattr(settings, var):
        self.settings[var] = settings.__getattr__(var)
  
  def authenticate(self, username=None, password=None):
    if len(password) == 0:
      return None
    else:
      from xtk.xtk_naga import compute
      if compute(
          "localhost", 10000, 'ri.lib.contest_naga', 'ldap_authenticate', username, password, 
          self.settings):
        return self.get_or_create_user(username, password)
      else:
          return None

  def get_or_create_user(self, username, password):
    try:
      return self._get_user_by_name(username)
    except User.DoesNotExist:
      return self._create_user(username, password)
    
  def _get_user_by_name(self, username):
    '''
    Returns an object of contrib.auth.models.User that has a matching username.
    called as: self._get_user_by_name(username)
    '''
    return User.objects.get(username=username)
    
  def _create_user(self, username, password):
    
    from xtk.xtk_naga import compute
    # results should have first_name, last_name, and email
    results = compute(
        "localhost", 10000, 'contest_naga', 'ldap_retrieve', username, password, 
        self.settings)
    # combine the results with other fields that we need to set.
    results.update(dict(username=username, is_staff=False, is_superuser=False))
    user = User(**results)
    user.set_password('ldap authenticated')
    user.save()
    return user

  def get_user(self, user_id):
    try:
      return User.objects.get(pk=user_id)
    except User.DoesNotExist:
      return None


