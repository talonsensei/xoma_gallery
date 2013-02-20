import pdb
import logging
import ldap
  
def ldap_authenticate(username, password, ldap_settings):
  """Authenticates a user against an LDAP server."""
  l = _ldap_login(username, password, ldap_settings)
  if l:
    _ldap_logout(l)
    return True
  else:
    return False
  

def ldap_retrieve(username, password, ldap_settings):
  """Retrieves the email, first name, and last name for a user from and LDAP server."""
  l = _ldap_login(username, password, ldap_settings, False)
  # search
  AD_SEARCH_FIELDS = ['mail','givenName','sn','sAMAccountName']
  result = l.search_ext_s(
      ldap_settings['AD_SEARCH_DN'], ldap.SCOPE_SUBTREE,
      "sAMAccountName=%s" % username, AD_SEARCH_FIELDS)[0][1]
      
  email = result['mail'][0] if result.has_key('mail') else 'no-mail@xoma.com'
  last_name = result['sn'][0] if result.has_key('sn') else None
  first_name = result['givenName'][0] if result.has_key('givenName') else None
  _ldap_logout(l)
  
  return {'email': email, 'last_name': last_name, 'first_name': first_name}

def _ldap_login(username, password, ldap_settings, simple=True):
  """Logs into the LDAP server and returns an LDAP connection.
  
  Arguments:
    username - self explanatory
    password - self explanatory
    ldap_settings - dictionary. expects the keys AD_CERT_FILE, AD_LDAP_URL, 
      and AD_NT4_DOMAIN to be set
    simple - boolean indicates whether it should use simple bind or not
  """
  try:
    # initialize connection
    ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, ldap_settings['AD_CERT_FILE'])
    ldap.set_option(ldap.OPT_X_TLS_CACERTDIR, ldap_settings['AD_CERT_PATH'])
    if not simple:
      ldap.set_option(ldap.OPT_REFERRALS,0) # DO NOT TURN THIS OFF OR SEARCH WON'T WORK!
    ldap_connection = ldap.initialize(ldap_settings['AD_LDAP_URL'])
    ldap_connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
    # bind
    binddn = "%s@%s" % (username, ldap_settings['AD_NT4_DOMAIN'])
    if simple:
      ldap_connection.simple_bind_s(binddn, password)
    else:
      ldap_connection.bind_s(binddn,password)
    return ldap_connection
  except (ImportError, ldap.INVALID_CREDENTIALS):
    return False

def _ldap_logout(ldap_connection):
  """Logs out of the LDAP server.
  
  Arguments:
    ldap_connection - an ldap connection created by _ldap_login
  """
  ldap_connection.unbind_s()