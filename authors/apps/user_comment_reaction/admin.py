from django.contrib import admin

# local imports
from authors.apps.user_comment_reaction.models import UserReactionOnComment

# Register your models here.
admin.site.register(UserReactionOnComment)
