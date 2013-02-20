from django.contrib import admin
from django import forms
from django.utils.datastructures import SortedDict
import photos.models as photos_m
import pdb

class CategoryInline(admin.TabularInline):
  model = photos_m.Category
  list_display = ('name', 'description', 'contest', 'photo_limit')
  max_num = 3
    
    
class AwardInline(admin.TabularInline):
  model = photos_m.Award
  fields = ['name']
  max_num = 5
  
  
class ContestAdmin(admin.ModelAdmin):
  list_display = ('name', 'submission_start', 'submission_end', 'voting_start', 'voting_end')
  inlines = (CategoryInline, AwardInline)

class WinnerInline(admin.TabularInline):
  model = photos_m.Winner
  
class EntryAdmin(admin.ModelAdmin):
  list_display = (
      'admin_thumbnail_html', 'owner', 'contest', 'category', 'total_score', 'total_votes', 
      'average_score', 'awards_list')
  list_filter = ('category',)
  search_fields = ('name','category__name', 'category__contest__name', 'owner__username')
  inlines = (WinnerInline, )


admin.site.register(photos_m.Contest, ContestAdmin)
admin.site.register(photos_m.Entry, EntryAdmin)
admin.site.register(photos_m.EntryUpload)