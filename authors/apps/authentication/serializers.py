from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from authors.apps.authentication.backends import JWTAuthentication
from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    def __init__(self, *args, **kwargs):
        super(RegistrationSerializer, self).__init__(*args, **kwargs)

        # Override the default error_messages with a custom field error
        for field in self.fields:
            error_messages = self.fields[field].error_messages
            error_messages['null'] = error_messages['blank'] \
                = error_messages['required'] \
                = 'Please fill in the {}.'.format(field)

    # Ensure the username entered is unique and has a descriptive error message
    # when a duplicate username is entered and an invalid username.
    username = serializers.RegexField(
        regex='^[A-Za-z\-\_]+\d*$',
        min_length=4,
        max_length=30,
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='The username already exists. Kindly try another.'
        )],
        error_messages={
            'min_length': 'Username must have a minimum of 4 characters.',
            'max_length': 'Username must have a maximum of 30 characters.',
            'invalid': 'Username cannot only have alphanumeric characters.'
        }
    )

    # Ensure the email entered is unique and has a descriptive error message
    # when a duplicate email is entered and an invalid email address.
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Email already exists. Sign in instead or try another.'
        )],
        error_messages={
            'invalid': 'You have input an invalid email. Kindly check again.'
        }
    )

    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and can not be read by the client.
    password = serializers.RegexField(
        regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[\!\@#\$%\^&]).*',
        max_length=128,
        min_length=8,
        write_only=True,
        error_messages={
            'max_length': 'Password must have a maximum of 128 characters.',
            'min_length': 'Password must have a minimum of 8 characters.',
            'invalid': 'Password must contain at least a lowercase letter, '
                       'an uppercase letter, a number and a special '
                       'character.'
        })

    token = serializers.SerializerMethodField()
    refresh_token = serializers.SerializerMethodField()

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['email', 'username', 'password', 'token', 'refresh_token']

    def create(self, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user.
        return User.objects.create_user(**validated_data)

    def get_token(self, obj):
        """
        generate an encoded JWT token
        :param obj:
        :return token:
        """
        return JWTAuthentication.generate_token(
            user=obj, is_refresh_token=False)

    def get_refresh_token(self, obj):
        """
        Generate a refresh token
        :return refresh token:
        """
        return JWTAuthentication.generate_token(
            user=obj, is_refresh_token=True)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    token = serializers.SerializerMethodField()
    refresh_token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'token', 'refresh_token')

    def get_token(self, obj):
        """
        generate an encoded JWT token by taking the user object
        :param obj:
        :return token:
        """
        return JWTAuthentication.generate_token(
            user=obj, is_refresh_token=True)

    def get_refresh_token(self, obj):
        """
        fetch and return refresh token
        :return:
        """
        return JWTAuthentication.generate_token(
            user=obj, is_refresh_token=False)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        # As mentioned above, an email is required. Raise an exception if an
        # email is not provided.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # As mentioned above, a password is required. Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value. Remember that, in our User
        # model, we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.

        return user


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so let's just stick with the defaults.
    password = serializers.RegexField(
        regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[\!\@#\$%\^&]).*',
        max_length=128,
        min_length=8,
        write_only=True,
        error_messages={
            'max_length': 'Password must have a maximum of 128 characters.',
            'min_length': 'Password must have a minimum of 8 characters.',
            'invalid': 'Password must contain at least a lowercase letter, '
                       'an uppercase letter, a number and a special '
                       'character.'
        })

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is because
        # we don't need to specify anything else about the field. For the
        # password field, we needed to specify the `min_length` and
        # `max_length` properties too, but that isn't the case for the token
        # field.

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # This is because Django provides a function that handles hashing and
        # salting passwords, which is important for security. What that means
        # here is that we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()` is the method mentioned above. It handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # Finally, after everything has been updated, we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        return instance
