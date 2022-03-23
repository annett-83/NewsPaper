from django.core.management.base import BaseCommand, CommandError
from news.models import Post




class Command(BaseCommand):
    help = 'Подсказка вашей команды'  # показывает подсказку при вводе "python manage.py <ваша команда> --help"
#    missing_args_message = 'Недостаточно аргументов'
#    requires_migrations_checks = True  # напоминать ли о миграциях. Если тру — то будет напоминание о том, что не сделаны все миграции (если такие есть)

    # def add_arguments(self, parser):
    #     # Positional arguments
    #     parser.add_argument('argument', nargs='?', type=str)

    def handle(self, *args, **options):
        # здесь можете писать любой код, который выполняется при вызове вашей команды
        self.stdout.readable()
        self.stdout.write(
            'Do you really want to delete all posts? yes/no')  # спрашиваем пользователя действительно ли он хочет удалить все товары
        answer = input()  # считываем подтверждение

        if answer == 'yes':  # в случае подтверждения действительно удаляем все товары
            Post.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Succesfully wiped Post!'))
            return

        self.stdout.write(self.style.ERROR('Access denied'))  # в случае неправильного