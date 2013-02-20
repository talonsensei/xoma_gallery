from django.db import models


COST_CHOICES = ((0, 'cheap'), (1, 'average'), (2, 'expensive'))
DISTANCE_CHOICES = ((0, 'walking'), (1, 'driving'))
QUALITY_CHOICES = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))
# Create your models here.
class Option(models.Model):
  '''(Option description)'''
  name = models.CharField(max_length=50)
  cost = models.IntegerField(choices=COST_CHOICES)
  distance = models.IntegerField(choices=DISTANCE_CHOICES)
  quality = models.IntegerField(choices=QUALITY_CHOICES)

  def __unicode__(self):
    return "Option"
