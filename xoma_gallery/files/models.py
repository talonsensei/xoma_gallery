import base64
import pdb
import tempfile
from PIL import Image as pil_Image

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile, File
from django.core.files.images import ImageFile
from django.core.files.storage import Storage
from django.db import models

from lib.core import nested_property

class FileContent(models.Model):
  '''
  Only contains binary data for the file.  All other data (size, name, etc.) is
  stored in the FileRecord model.  The binary data is base64 encoded and stored
  in a TextField.
  '''
  
  content = models.TextField()


class DatabaseStorage(Storage):
  '''
  This custom storage manager automatically handles storing files in the database
  instead of in the local file system.  Files are encoded in base64 and stored in
  a text field.
  '''
  
  def _open(self, name, mode=None):
    '''
    Returns a ContentFile object containing the requested file.
    
    Arguments:
    name - Primary key of the file's database entry.
    mode - This is not used but must be included to ensure compatibility
           with other Django modules.
    '''
    f = FileContent.objects.get(pk=name)
    data = base64.b64decode(f.content)
    
    return ContentFile(data)
      
  def _save(self, name, content):
    '''
    Saves a file to the database.
    
    Arguments:
    name - Primary key to use when storing the file.
    content - A python file object to be saved.  Actually, content will most
              likely be an object that inherits from a python file object.
    '''
    try:
      # get existing file if it exists
      f = FileContent.objects.get(pk=name)
    except ObjectDoesNotExist:
      # otherwise, create a new file
      f = FileContent()
      f.pk = name
        
    # for an unknown reason, we must reset the current reading location
    content.seek(0)
    f.content = base64.b64encode(content.read())
    f.save()
    
    return str(name)
      
  def size(self, name):
    f = FileContent.objects.get(pk=name)
    return len(base64.b64decode(f.content))
      
  def exists(self, name):
    return bool(FileContent.objects.get(pk=name))
      
  def delete(self, name):
    if self.exists(name):
      FileContent.objects.get(pk=name).delete()
          
  def url(self, name):
    return '/contest/files/%s' % name
      
  def get_available_name(self, name=None):
    '''
    Returns the next available primary key. Does not take the provided name
    into account in any way.
    '''
    try:
      next_pk = FileContent.objects.order_by('-pk')[0].pk + 1
    except IndexError:
      # in case there are no files in the database
      next_pk = 1
        
    self.my_val = name
    return str(next_pk)


# this is used in FileRecord, but created here to avoid multiple instances
db_storage = DatabaseStorage()

class FileRecord(models.Model):
  '''
  Contains all of the extra data associated with a file.  Stores file size, name,
  label, and content type for all files.  Also caches width and height for images.
  '''
  
  _doc_contents = models.FileField(upload_to='docs', storage=db_storage, blank=True, null=True)
  _img_contents = models.ImageField(upload_to='imgs', storage=db_storage, blank=True, null=True)
  _name = models.CharField(max_length=255)
  _size = models.IntegerField()
  _width = models.IntegerField(blank=True, null=True)
  _height = models.IntegerField(blank=True, null=True)
  mime_type = models.CharField(max_length=50)
  label = models.CharField(max_length=100, blank=True, null=True)
  # parent
  content_type = models.ForeignKey(ContentType)
  object_id = models.IntegerField()
  parent = generic.GenericForeignKey('content_type', 'object_id')
  # end parent
  
  def __init__(self, *args, **kwargs):
    '''
    Allows the user to set the contents in the constructor using an optional
    keyword argument.  This is neccessary because contents is a property, not
    a field.
    
    Arguments:
    contents - Either a File or and ImageFile object that is to be stored.
               This can only be given as a keyword argument.
    '''
    # save and remove extra kwargs so super.__init__ doesn't get confused
    if 'contents' in kwargs:
      contents = kwargs['contents']
      del(kwargs['contents'])
    else:
      contents = None
      self.new_contents = None
        
    # super.__init__ must be called before contents is set, otherwise the
    # fields set in the contents property (_name, _size, etc.) will be reset
    # by super.__init__
    
    super(FileRecord, self).__init__(*args, **kwargs)
    
    if contents:
      self.contents = contents
      
  @nested_property
  def contents():
    '''
    Handles setting and returning _doc_contents, _img_contents, or new_contents.
    new_contents is returned if the contents have been changed but not saved.
    Otherwise, _doc_contents or _img_contents is returned.  fset takes either a
    File or an ImageFile object and sets _name, _size, _width, and _height.
    '''
            
    def fget(self):
      return self.new_contents or self._doc_contents or self._img_contents
          
    def fset(self, value):
      self.new_contents = value
      if self.image_contents:
        self._width = value.width
        self._height = value.height
      else:
        self._width = None
        self._height = None
      self._name = value.name
      self._size = value.size
          
    return locals()

  @property
  def image_contents(self):
    """boolean indicates whether this FileRecord has image contents"""
    return "image/" in self.mime_type
    
  @property
  def url(self):
    """URL to get the contents of this instance."""
    return '%s.%s' % (self.contents.url, self.ext)
    
  @property
  def ext(self):
    mime_to_ext = {
      'image/gif': 'gif', 
      'image/jpeg': 'jpg', 
      'image/jpg': 'jpg',
      'image/png': 'png', 
      'image/tiff': 'tiff'
    }
    return mime_to_ext[self.mime_type.lower()]
      
  # users should be able to see but not set the following properties, which
  # are automatically set when the contents are set
  @property
  def name(self):
    return self._name
      
  @property
  def size(self):
    return self._size
      
  @property
  def width(self):
    return self._width
      
  @property
  def height(self):
    return self._height
  
  def generate_thumbnail(self, dimensions, label='thumbnail'):
    try:
      old_thumb = FileRecord.objects.get(
          label=label, content_type=self.content_type, object_id=self.object_id)
      old_thumb.delete()
    except FileRecord.DoesNotExist:
      pass
    
    im = pil_Image.open(self.contents)
    # create thumbnail
    im = self._crop_and_resize(im, dimensions)
    # write thumbnail to a temporary file
    tempf = tempfile.NamedTemporaryFile()
    im.save(tempf, format="png")
    # rewind the temp file
    tempf.seek(0)
    # create a new ImageFile instance using the temporary file
    imagef = ImageFile(tempf)
    # create the thumbnail as a file record with the label
    new_thumb = FileRecord(
        contents=imagef, mime_type="image/png", label=label, content_type=self.content_type,
        object_id=self.object_id)
    new_thumb.save()
    
  
  def _crop_and_resize(self, image, dimensions):
    '''Crops and resizes the image to the given dimensions.

    Code taken and modified from the Photologue plugin for Django 
    (http://code.google.com/p/django-photologue/).

    Arguments:
      image - a PIL image
      dimensions - a tuple containing width and height in that order.
    Returns:
      copy of image that is resized and cropped.
    '''
    w, h = image.size
    new_w, new_h = dimensions
    # select the aspect ratio
    ratio = max(float(new_w)/w, float(new_h)/h)
    x = (w * ratio)
    y = (h * ratio)
    # number of pixels that should be removed from right/left and top/bottom
    x_diff = int(abs(new_w - x) / 2)
    y_diff = int(abs(new_h - y) / 2)
    # box is a centered crop
    box = (int(x_diff), int(y_diff), int(x_diff + new_w), int(y_diff + new_h))
    return image.resize((int(x), int(y)), pil_Image.ANTIALIAS).crop(box)
      
        
def file_record_pre_save(sender, instance, **kwargs):
  '''
  If the contents have been updated, then any old contents are deleted from the
  filesystem and the new contents are saved.
  '''
    
  if instance.new_contents:
    # only one of these should ever be set
    old_contents = instance._doc_contents or instance._img_contents
    if old_contents:
      old_contents.delete()
    
    if instance.image_contents:
      instance._img_contents.save(instance.name, instance.new_contents, save=False)
    else:
      instance._doc_contents.save(instance.name, instance.new_contents, save=False)
        
    instance.new_contents = None
        
models.signals.pre_save.connect(file_record_pre_save, sender=FileRecord)