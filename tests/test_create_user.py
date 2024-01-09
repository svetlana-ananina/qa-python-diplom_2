import pytest
import allure

from data import StatusCodes as CODE
from data import ResponseKeys as KEYS
from data import ResponseMessages as message
from helpers.helpers_on_check_response import HelpersOnCheck as c
from helpers.helpers_on_create_user import HelpersOnCreateUser as u


class TestCreateUser:

    @pytest.fixture
    def setup_user(self):
        # Инициализируем данные пользователя для удаления после завершения работы
        self.to_teardown = False        # Выполнять удаление созданного пользователя
        self.user_data = None
        self.auth_token = None
        self.refresh_token = None

        yield
        # Удаляем созданного пользователя
        if self.to_teardown:
            u.try_to_delete_user(self.auth_token)


    def __init_teardown(self, user_data, auth_token, refresh_token):
        """
        Сохраняем полученные данные пользователя
        """
        self.user_data = user_data.copy()
        self.to_teardown = True
        self.auth_token = auth_token
        self.refresh_token = refresh_token


    @allure.title('Проверка создания пользователя - регистрация уникального пользователя')
    def test_create_user_new_user(self, setup_user):
        # генерируем уникальные данные нового пользователя: email, password, user_name
        user_data = u.generate_random_user_data()

        # отправляем запрос на создание пользователя и проверяем полученные данные
        auth_token, refresh_token = u.create_and_check_user(user_data)

        # сохраняем полученные данные пользователя
        self.__init_teardown(user_data, auth_token, refresh_token)


    @allure.title('Проверка создания пользователя - повторная регистрация пользователя')
    def test_create_user_double_user_error(self, setup_user):
        # генерируем уникальные данные нового пользователя: email, password, user_name
        user_data = u.generate_random_user_data()
        # отправляем запрос на создание пользователя
        auth_token, refresh_token = u.create_user(user_data)
        # сохраняем полученные данные пользователя
        self.__init_teardown(user_data, auth_token, refresh_token)
        # отправляем повторный запрос на создание того же пользователя
        response = u.try_to_create_user(user_data)

        # проверяем что получен код ответа 403
        # проверяем в теле ответа: { "success" = False }
        # проверяем сообщение в теле ответа: { "message" = "User already exists" }
        c.check_not_success_error_message(response, CODE.FORBIDDEN, message.USER_ALREADY_EXISTS)


    @allure.title('Проверка создания пользователя - не заполнено одно из полей')
    @pytest.mark.parametrize('field', [         # незаполненное поле
        KEYS.EMAIL_KEY,
        KEYS.PASSWORD_KEY,
        KEYS.NAME_KEY
    ])
    def test_create_user_empty_field_error(self, setup_user, field):
        # генерируем уникальные данные нового пользователя: email, password, user_name
        user_data = u.generate_random_user_data()
        # удаляем поле field
        user_data.pop(field)
        # отправляем запрос на создание пользователя
        response = u.try_to_create_user(user_data)

        # проверяем что получен код ответа 403
        # проверяем в теле ответа: { "success" = False }
        # проверяем сообщение в теле ответа: { "message" = "Email, password and name are required fields" }
        c.check_not_success_error_message(response, CODE.FORBIDDEN, message.MISSING_REQUIRED_FIELD)

