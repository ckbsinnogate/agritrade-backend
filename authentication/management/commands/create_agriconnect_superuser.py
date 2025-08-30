"""
AgriConnect Custom Superuser Creation Command
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from getpass import getpass
import sys

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with email or phone number for AgriConnect'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            dest='email',
            help='Email address for the superuser',
        )
        parser.add_argument(
            '--phone',
            dest='phone',
            help='Phone number for the superuser (e.g., +233273735500)',
        )
        parser.add_argument(
            '--password',
            dest='password',
            help='Password for the superuser',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        phone = options.get('phone')
        password = options.get('password')

        # Get identifier (email or phone)
        if not email and not phone:
            while True:
                identifier = input('Email or Phone Number: ').strip()
                if not identifier:
                    self.stderr.write('This field cannot be blank.')
                    continue
                
                if '@' in identifier:
                    email = identifier
                elif identifier.startswith('+') or identifier.replace(' ', '').replace('-', '').isdigit():
                    phone = identifier
                else:
                    self.stderr.write('Please enter a valid email or phone number (e.g., +233273735500)')
                    continue
                break

        # Get password
        if not password:
            while True:
                password = getpass('Password: ')
                if not password:
                    self.stderr.write('This field cannot be blank.')
                    continue
                password2 = getpass('Password (again): ')
                if password != password2:
                    self.stderr.write("Error: Your passwords didn't match.")
                    continue
                break

        try:
            # Determine identifier
            identifier = email if email else phone
            
            # Create superuser
            user = User.objects.create_superuser(
                username=identifier,  # Pass as username for Django compatibility
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Superuser created successfully!')
            )
            self.stdout.write(f'Username: {user.username}')
            if user.email:
                self.stdout.write(f'Email: {user.email}')
            if user.phone_number:
                self.stdout.write(f'Phone: {user.phone_number}')
                
        except Exception as e:
            raise CommandError(f'Error creating superuser: {e}')
