from django.db import models

# Create your models here.


class Book(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)  # blank=True ==> means that it is not required
    blurb = models.TextField(blank=True)
    num_pages = models.IntegerField(blank=True)
    price = models.FloatField(blank=True)
    in_print = models.BooleanField(default=True)

    website = models.URLField(blank=True, null=True)

    date_printed = models.DateField(blank=True, null=True)

    publisher = models.ForeignKey('Publisher', blank=True, null=True, on_delete=models.CASCADE)

    authors = models.ManyToManyField('Author')

    genres = models.ManyToManyField('Genre')

    sample_chapter = models.FileField(blank=True, null=True, upload_to='chapters/%Y/%m/%d/')
    # /%Y/%m/%d/ is optional; represents 2018/01/21;
    # FileField stores files (.txt, .pdf, .doc)

    cover_image = models.ImageField(blank=True, null=True, upload_to='covers/%Y/%m/%d/')
    # ImageField stores a specif type of file: images (.png, .gif, .jpg)
    # Requires Pillow: pip install Pillow

    def __str__(self):
        return self.title


class Publisher(models.Model):
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title


class Author(models.Model):
    given_name = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255)

    def __str__(self):
        return self.family_name + ', ' + self.given_name


class Genre(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title