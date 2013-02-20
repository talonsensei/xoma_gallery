import datetime
import pdb
from PIL import Image as pil_Image
import tempfile
import os
import random

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.files.images import ImageFile
from django.core.files.base import ContentFile
from django.db.models import signals

import files.models as files_m
from lib.core import nested_property

THUMBNAIL_SIZE = (200, 150)

class Contest(models.Model):
  '''The particular contest.
  
  Usually something like Spring 2008, Fall 2007, etc.
  '''
  name = models.CharField(max_length=50)
  submission_start = models.DateField(default=datetime.date.today)
  submission_end = models.DateField(blank=True, null=True)
  voting_start = models.DateField(blank=True, null=True)
  voting_end = models.DateField(blank=True, null=True)
  
  @property
  def voting_on(self):
    """Determines whether voting is on or not."""
    return not self.voting_end or datetime.date.today() < self.voting_end

  @property
  def winners(self):
    return Winner.objects.filter(award__contest=self)
  
  def sample_entries(self):
    photos = []
    for cat in self.categories.all():
      pos = random.randint(0, cat.entries.all().count() - 1)
      photos.append(cat.entries.all()[pos])
    return photos

  def __unicode__(self):
    return self.name
  
  class Meta:
    ordering = ['-submission_end']

class Category(models.Model):
  '''The different categories of a particular contest. 
  
  Usually something like flowers, portraits, blue, etc. The photo_limit indicates
  how many photos a particular user is allowed to have.
  '''
  name = models.CharField(max_length=50)
  description = models.TextField(blank=True)
  contest = models.ForeignKey(Contest, related_name='categories')
  photo_limit = models.IntegerField(blank=True, null=True)

  def __unicode__(self):
    return self.name
    
  class Meta:
    verbose_name_plural = 'categories'
    ordering = ['name']
    
class Entry(models.Model):
  '''The photo entry for a particular user in a category. 
  
  For example Mark Evans would have a photo for the flowers category, which 
  belongs to a particular contest.
  '''
  name = models.CharField(max_length=100)
  owner = models.ForeignKey(User, related_name='entries')
  category = models.ForeignKey(Category, related_name='entries')
  _images = generic.GenericRelation(files_m.FileRecord)
  
  @nested_property
  def image():
    """Property that allows _images to be treated as a single image."""
    def fget(self):
      try:
        return self._images.get(label="normal")
      except files_m.FileRecord.DoesNotExist:
        return None
    def fset(self, value):
      # delete existing image
      if self.image:
        self.image.delete()
      self._images.create(contents=value, mime_type=value.content_type, label='normal')
      self.refresh_thumbnail()
      
    return locals()
    
  @property
  def thumbnail(self):
    """Return the thumbnail for the image."""
    try:
      return self._images.get(label="thumbnail")
    except files_m.FileRecord.DoesNotExist:
      return None

  @property
  def contest(self):
    return self.category.contest
    
  @property
  def total_votes(self):
    return self.votes.all().count()
    
  @property
  def total_score(self):
    return sum([vote.score for vote in self.votes.all()])
    
  @property
  def average_score(self):
    try:
      return u"%.02f" % (float(self.total_score) / float(self.total_votes))
    except ZeroDivisionError:
      return 0
      
  @property
  def awards_list(self):
    awards_list = ["%s (%d)" % (winner.award.name, winner.place) for winner in self.winners.all()]
    return ", ".join(awards_list)
  
  def admin_thumbnail_html(self):
    return u"<img src=%s height='75' width='100' />" % self.thumbnail.url
  admin_thumbnail_html.short_description = 'Thumbnail'
  admin_thumbnail_html.allow_tags = True
    
  def refresh_thumbnail(self):
    self.image.generate_thumbnail(dimensions=THUMBNAIL_SIZE)
  
  def __unicode__(self):
    return "%s by %s" % (self.name, self.owner)

  class Meta:
    verbose_name_plural = 'entries'
    ordering = ['-category__contest__voting_end']
    
class EntryUpload(models.Model):
  '''Used to upload photos in admin interface.
  
  Deleted after the Entry object is created.'''
  name = models.CharField(max_length=100, null=True, blank=True)
  owner = models.ForeignKey(User)
  category = models.ForeignKey(Category)
  image = models.ImageField(upload_to="tmp_photos")

  def __unicode__(self):
    return "EntryUpload"

def entryupload_post_save(sender, instance, **kwargs):
  '''Creates an Entry instance and deletes the EntryUpload instance.'''
  if instance.name:
    name = instance.name 
  else:
    name, ext = os.path.splitext(os.path.basename(instance.image.path))
  entry = Entry(name=name, owner=instance.owner, category=instance.category)
  entry.save()
  img = ImageFile(open(instance.image.path))
  img.content_type = content_type(os.path.basename(img.name))
  entry.image = img
  instance.delete()

signals.post_save.connect(entryupload_post_save, sender=EntryUpload)

class Vote(models.Model):
  '''Represents a vote by a particular vote on a particular photo entry.'''
  
  SCORE_CHOICES = [(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'),
      (9, '9'), (10, '10')]
    
  entry = models.ForeignKey(Entry, related_name="votes")
  voter = models.ForeignKey(User, related_name="votes")
  score = models.IntegerField(choices=SCORE_CHOICES)
    
  def __unicode__(self):
    return "%s gave %s a %d" % (self.voter, self.entry.name, self.score)
        
  def save(self, *args, **kwargs):
    try:
      self.score = int(self.score)
    except:
      pass
        
    super(Vote, self).save(*args, **kwargs)
        
  class Meta:
    unique_together = ("entry", "voter")
    verbose_name_plural = "votes"


class Award(models.Model):
  """Awards are given to the entries.
  
  This is manually decided. Although they are based on the points that a 
  particular entry gets, it's possible that other criteria may be used as 
  well (such as whether or not an entry's photographer has taken another 
  photo or not).
  """
  contest = models.ForeignKey(Contest, related_name="awards")
  name = models.CharField(max_length=30, unique=False)
  description = models.TextField(blank=True)
  
  def __unicode__(self):
    return "%s (%s)" % (self.name, self.contest.name)
    
  @property
  def winners_list(self):
    return ", ".join([winner.entry.name for winner in self.winners])
      
  def photos(self):
    return [ag.photo for ag in self.winners.all()]
  
  def list_display_photos(self):
    photo_names = [p.__unicode__() for p in self.photos()]
    return ', '.join(photo_names)
  list_display_photos.short_description = "Photos that received this award"
  
  class Meta:
    ordering = ['-contest__voting_end', 'name']
    
            
class Winner(models.Model):
  """A winner is a join model that connects awards with winners.
  
  It has an additional attribute called place that indicates what place a
  particular entry is in. For example their could be a 1st, 2nd, and 3rd place
  entry for one award.
  """
  entry = models.ForeignKey(Entry, related_name="winners")
  award = models.ForeignKey(Award, related_name='winners')
  place = models.IntegerField(
      help_text="how the photo placed in the award (i.e. 1st place would be 1)", blank=True)
  
  class Meta:
    ordering = ['award', 'place']

# === HELPER FUNCTIONS ===
def content_type(filename):
  prefix, ext = os.path.splitext(filename)
  ext = ext[1:] if ext != '.jpg' else 'jpeg'
  return "image/%s" % ext