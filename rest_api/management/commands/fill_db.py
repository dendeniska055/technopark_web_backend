from django.core.management.base import BaseCommand, CommandError
from rest_api.models import User, Publication, Comment, Like, Tag, Subscription
import json
from datetime import datetime, timedelta
from django.db.models import Q
import mimesis
from random import randint
from time import sleep

users_count = 10**2
publication_count = 10**2
comment_count = 10**3
like_count = 10**4
tags_count = 10**2
# users_count = 10**4
# publication_count = 10**5
# comment_count = 10**6
# like_count = 2*10**6
# tags_count = 10**4
tags_publ_count = 50

seconds_sleep = 2
count_to_sleep = 500


def gen_tag():
    lang = randint(0, 1)
    if lang == 0:
        lang = 'ru'
    else:
        lang = 'en'

    word_count = randint(1, 3)
    words = mimesis.Text(lang).words(quantity=word_count)
    return '_'.join(words)


def this_sleep(i):
    if i % count_to_sleep == 0:
        print('sleep', seconds_sleep,
              'sec, чтобы не было переполнения памяти')
        sleep(seconds_sleep)


class Command(BaseCommand):
    help = 'Заполняет БД тестовыми записями'

    def handle(self, *args, **options):
        get_users_count = User.objects.all().count()
        print('users_count:', get_users_count)
        sleep(2)
        for i in range(users_count - get_users_count):
            User.objects.create(
                name=mimesis.Person('en').username(),
                birthday=mimesis.Datetime().date(start=1950, end=2002),
                registration_date=mimesis.Datetime().datetime(),
                email=mimesis.Person('en').email(),
                description=mimesis.Text('ru').sentence()
            )
            this_sleep(i)
            print('users_count:', get_users_count + i, ' из ', users_count)

        get_publication_count = Publication.objects.all().count()
        print('publication_count:', get_publication_count)
        sleep(1)
        for i in range(publication_count - get_publication_count):
            Publication.objects.create(
                description=mimesis.Text('ru').sentence(),
                author=User.objects.get(pk=randint(1, users_count-2)),
                title=mimesis.Text('ru').title()
            )
            this_sleep(i)
            print('publication_count:', get_publication_count +
                  i, 'из', publication_count)

        get_comment_count = Comment.objects.all().count()
        print('comment_count:', get_comment_count)
        sleep(1)
        for i in range(comment_count - get_comment_count):
            Comment.objects.create(
                author=User.objects.get(pk=randint(1, users_count-2)),
                publication=Publication.objects.get(pk=randint(1, publication_count-2)),
                comment=mimesis.Text('ru').sentence()
            )
            this_sleep(i)
            print('comment_count:', get_comment_count + i, 'из', comment_count)

        get_like_count = Like.objects.all().count()
        print('like_count:', get_like_count)
        sleep(1)
        for i in range(like_count - get_like_count):
            if randint(0, 1):
                Like.objects.create(
                    author=User.objects.get(pk=randint(1, users_count-2)),
                    publication=Publication.objects.get(pk=randint(1, publication_count-2))
                )
            else:
                Like.objects.create(
                    author=User.objects.get(pk=randint(1, users_count-2)),
                    comment=Comment.objects.get(randint(1, comment_count-2))
                )
            this_sleep(i)
            print('like_count:', get_like_count + i, 'из', like_count)

        get_tags_count = Tag.objects.all().count()
        print('tags_count:', get_tags_count)
        sleep(1)
        for i in range(tags_count - get_tags_count):
            tag = Tag(title=gen_tag())
            tag.save()
            for j in range(1, tags_publ_count):
                tag.publication.add(Publication.objects.get(
                    pk=randint(1, publication_count-2)))
            tag.save()
            this_sleep(i)
            print('tags_count:', get_tags_count + i, 'из', tags_count)

        # need_date = (datetime.now() + timedelta(days=10)).date()
        # payouts_types = Payouts_type.objects.filter(date_end=need_date)
        # if len(payouts_types) > 0:
        #     message = "Через 10 дней закончится прием следующих заявлений: " + \
        #         ', '.join([ payout_type.payouts_type for payout_type in payouts_types])
        #     self.stdout.write(message)
        #     admins = Students.objects.filter(proforg__gte=3).exclude(vk_id="")
        #     if len(admins) > 0:
        #         message_send({
        #             'user_ids': ','.join([ admin.vk_id for admin in admins]),
        #             'message': message,
        #         })
        # self.stdout.write('Successfully test')
        return
