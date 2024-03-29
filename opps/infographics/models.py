# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from taggit.managers import TaggableManager

from opps.core.models import Publishable, BaseBox, BaseConfig


class Infographic(Publishable):

    TYPES = (
        ("gallery", _(u"Photo Gallery")),
        ("css", _(u"Custom CSS")),
        ("timeline", _(u"Timeline")),
    )
    title = models.CharField(_(u"Title"), max_length=255)
    slug = models.SlugField(
        _(u"URL"),
        max_length=150,
        unique=True,
        db_index=True
    )
    headline = models.TextField(_(u"Headline"), blank=True, null=True)
    description = models.TextField(
        _(u"Description"),
        blank=True,
        null=True,
        help_text=_(u'Main description, also used by timeline type')
    )
    channel = models.ForeignKey(
        'channels.Channel',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    posts = models.ManyToManyField(
        'articles.Post',
        null=True,
        blank=True,
        related_name='infographic_post',
        through='InfographicPost'
    )
    top_image = models.ForeignKey(
        'images.Image',
        verbose_name=_(u'Infographic Top Image'), blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='infographic_topimage'
    )
    main_image = models.ForeignKey(
        'images.Image',
        verbose_name=_(u'Infographic Image'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='infographic_image'
    )

    order = models.IntegerField(_(u"Order"), default=0)
    tags = TaggableManager(blank=True)

    type = models.CharField(
        _(u"Infographic type"),
        max_length=20,
        choices=TYPES,
        default="gallery"
    )
    items = models.ManyToManyField(
        'infographics.InfographicItem',
        null=True, blank=True,
        related_name='infographic_item',
        through='InfographicInfographicItem'
    )

    # css
    css_path = models.CharField(
        _(u"Custom css path"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(u'/static/css/file.css or http://domain.com/file.css')
    )
    #    js_filepath
    js_path = models.CharField(
        _(u"Custom Java Script path"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(u'allowed only in the same domain')
    )

    # Timeline
    timeline = models.ForeignKey(
        'timelinejs.Timeline',
        verbose_name=_(u'Timeline'),
        null=True,
        blank=True,
        related_name='infographic_timeline',
        on_delete=models.SET_NULL,
        help_text=_(u'Set this and provide JSON, DOC or Events')
    )

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['order']


class InfographicInfographicItem(models.Model):
    item = models.ForeignKey(
        'infographics.InfographicItem',
        verbose_name=_(u'Infographic Item'),
        null=True,
        blank=True,
        related_name='infographicitem_item',
        on_delete=models.SET_NULL
    )
    infographic = models.ForeignKey(
        'infographics.Infographic',
        verbose_name=_(u'Infographic'),
        null=True,
        blank=True,
        related_name='infographicitem_infographic',
        on_delete=models.SET_NULL
    )

    def __unicode__(self):
        return u"{0}-{1}".format(self.infographic.slug, self.item.title)


class InfographicPost(models.Model):
    post = models.ForeignKey(
        'articles.Post',
        verbose_name=_(u'Infographic Post'),
        null=True,
        blank=True,
        related_name='infographicpost_post',
        on_delete=models.SET_NULL
    )
    infographic = models.ForeignKey(
        'infographics.Infographic',
        verbose_name=_(u'Infographic'),
        null=True,
        blank=True,
        related_name='infographicpost_infographic',
        on_delete=models.SET_NULL
    )

    def __unicode__(self):
        return u"{0}-{1}".format(self.infographic.slug, self.post.slug)


class InfographicItem(models.Model):
    title = models.CharField(_(u"Title"), max_length=255)
    slug = models.SlugField(
        _(u"URL"),
        max_length=150,
        db_index=True
    )
    description = models.TextField(_(u"Description"), null=True, blank=True)

    # optional for gallery and css
    group = models.CharField(
        _(u"Group"),
        max_length=255,
        blank=True, null=True,
        help_text=_(u'To group menu items or to store custom attributes')
    )

    image = models.ForeignKey(
        'images.Image',
        verbose_name=_(u'Infographic Item Image'),
        blank=True,
        null=True,
        help_text=_(u'Image'),
        on_delete=models.SET_NULL,
    )
    # gallery
    album = models.ForeignKey(
        'articles.Album',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='infographicitem_album',
        verbose_name=_(u'Album'),
    )

    timeline = models.ForeignKey(
        'timelinejs.Timeline',
        verbose_name=_(u'Timeline'),
        null=True,
        blank=True,
        related_name='infographicitem_timeline',
        on_delete=models.SET_NULL,
        help_text=_(u'Set this and provide JSON, DOC or Items')
    )

    order = models.IntegerField(_(u"Order"), default=0)

    def belongs(self):
        if not self.infographicitem_item.exists():
            return _(u"No infographic")

        return ", ".join(item.infographic.title for item in self.infographicitem_item.all())

    __unicode__ = lambda self: self.title


class InfographicBox(BaseBox):

    infographics = models.ManyToManyField(
        'infographics.Infographic',
        null=True, blank=True,
        related_name='infographicbox_infographics',
        through='infographics.InfographicBoxInfographics'
    )


class InfographicBoxInfographics(models.Model):
    infographicbox = models.ForeignKey(
        'infographics.InfographicBox',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='infographicboxinfographics_infographicboxes',
        verbose_name=_(u'Infographic Box'),
    )
    infographic = models.ForeignKey(
        'infographics.Infographic',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='infographicboxinfographics_infographics',
        verbose_name=_(u'Infographic'),
    )
    order = models.PositiveIntegerField(_(u'Order'), default=0)

    def __unicode__(self):
        return u"{0}-{1}".format(self.infographicbox.slug, self.infographic.slug)

    def clean(self):

        if not self.infographic.published:
            raise ValidationError(_(u'Infographic not published!'))

        if not self.infographic.date_available <= timezone.now():
            raise ValidationError(_(u'Infographic date_available '
                                    u'is greater than today!'))


class InfographicConfig(BaseConfig):

    infographic = models.ForeignKey(
        'infographics.Infographic',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='infographicconfig_infographics',
        verbose_name=_(u'Infographic'),
    )

    class Meta:
        permissions = (("developer", "Developer"),)
        unique_together = (
            "key_group", "key", "site",
            "channel", "article", "infographic"
        )
