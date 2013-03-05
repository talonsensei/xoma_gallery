from django.contrib import admin
import xoma_gallery.decider.models as dec_m

class OptionAdmin(admin.ModelAdmin):
  list_display = ('name', 'cost', 'distance', 'quality')

admin.site.register(dec_m.Option, OptionAdmin)
