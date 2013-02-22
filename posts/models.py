from django.db import models

# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField()
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return '/tag/' + self.slug + '/1/'

class Post(models.Model):
    datePosted = models.DateTimeField(null=True)
    lastUpdated = models.DateTimeField(auto_now=True)
    published = models.BooleanField()
    slug = models.SlugField()
    title = models.CharField(max_length=300)
    text = models.TextField()
    excerpt = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="posts")
    def get_absolute_url(self):
        if self.published:
            return '/' + self.slug
        else:
            print self.id
            return '/admin/posts/post/' + str(self.id) + '/'
    def __unicode__(self):
        return self.title
