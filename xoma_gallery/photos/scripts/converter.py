#!/usr/bin/env python
import datetime
import pdb
import re
import sys
import os
import pdb

def content_type(filename):
  prefix, ext = os.path.splitext(filename)
  ext = ext if ext != 'jpg' else 'jpeg'
  return "image/%s" % ext

def convert():
    '''Attempts to convert from the old system to users in the new system.
    
    Does not attempt to use LDAP to verify that the user exists in AD.
    '''    
    def create_user_if_not_present(first_name, last_name):
      username = last_name.lower()
      if not len(auth_m.User.objects.filter(username=username)):
        email = "%s@xoma.com" % username
        user = auth_m.User.objects.create_user(username, email, 'legacy')
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return user
      else:
        return auth_m.User.objects.get(username=username)
        
    def create_category_if_not_present(contest, category):
      category = category.strip(' "') # remove extra quotes and spaces
      con = photos_m.Contest.objects.get(name=contest)
      return photos_m.Category.objects.get_or_create(name=category, contest=con)[0]
    
    def create_entry_if_not_present(old_photo):
      if not len(photos_m.Entry.objects.filter(name=old_photo.title)):
        # get or create owner
        first_name, sep, last_name = old_photo.photographer.rpartition(' ')
        owner = create_user_if_not_present(first_name, last_name)
        # get or create category
        contest, category = old_photo.tags.split(' ', 1)
        category = create_category_if_not_present(contest, category)
        entry = photos_m.Entry(name=old_photo.title, owner=owner, category=category)
        entry.save()
        img = ImageFile(open(old_photo.image.path))
        img.content_type = content_type(os.path.basename(img.name))
        entry.image = img
        return entry
      else:
        return photos_m.Entry.objects.filter(name=old_photo.title)
    
    # create all the contests
    [c.delete() for c in photos_m.Contest.objects.all()]
    # create them again
    for old_gallery in pl_m.Gallery.objects.all():
      con = photos_m.Contest(name=old_gallery.tags)
      con.save()
    
    # clear out entries
    [e.delete() for e in photos_m.Entry.objects.all()]
    # create them again
    for old_photo in pl_m.Photo.objects.all():
      # create new photo entry from old photo
      sys.stdout.write('[P]'); sys.stdout.flush()
      entry = create_entry_if_not_present(old_photo)
      # go through all the old entries and convert them
      for old_entry in old_photo.entries.all():
        # create voter
        voter = create_user_if_not_present(old_entry.voter.first_name, old_entry.voter.last_name)
        # create vote from old entry
        vote = photos_m.Vote(entry=entry, voter=voter, score=old_entry.score)
        vote.save()
        sys.stdout.write('.'); sys.stdout.flush()
      # go through all the old winners
      for old_winner in old_photo.winners.all():
        # get contest - all contests should already be created
        contest = photos_m.Contest.objects.get(name=old_winner.award.gallery.tags)
        # get or create new award
        award = photos_m.Award.objects.get_or_create(
            name=old_winner.award.name, contest=contest, 
            description=old_winner.award.description)[0]
        # create new winner
        winner = photos_m.Winner(entry=entry, award=award, place=old_winner.place)
        winner.save()
        sys.stdout.write('w'); sys.stdout.flush()
    print
    print "--- Done"
    
    

def prepare_imports():
    """Makes it easy to create standalone scripts that reference Django modules"""    
    sys.path.append('/opt/local/var/apps/current/django/xoma_gallery')
    # set up the environment using the settings module
    from django.core.management import setup_environ
    import settings
    setup_environ(settings)

if __name__ == "__main__":
  prepare_imports()
  import django.contrib.auth.models as auth_m
  from django.core.files.images import ImageFile
  from django.db import connection

  import photos.models as photos_m
  import photologue.models as pl_m
  import voting.models as vot_m
  import files.models as files_m
  convert()
  