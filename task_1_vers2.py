from collections import UserDict
from datetime import datetime, timedelta
import pickle


# Друга версія коду без використання абстрактних класів, але з незалежним головним циклом програми, 
# бо його зміни, при необхідності, будуть вноситись в клас "назва класу"


def save_data(book, filename="addressbook_2.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook_2.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and 10 numbers phone please."
        except IndexError:
            return "Enter the argument for the command"
        except KeyError:
            return "Enter correct user name"
           
    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("The phone number must contain 10 digits")
        super().__init__(value)

    @staticmethod
    def validate_phone(value):
        return len(value) == 10 and value.isdigit()


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime('%d.%m.%Y')


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def delete_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}, birthday: {self.birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        days = 7
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if 0 <= (birthday_this_year - today).days <= days:
                    if birthday_this_year.weekday() >= 5:
                        birthday_this_year = self.find_next_weekday(birthday_this_year, 0)

                    congratulation_date_str = birthday_this_year.strftime('%d.%m.%Y')
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date_str
                    })
        return upcoming_birthdays

    @staticmethod
    def find_next_weekday(d: datetime, weekday: int):
        next_days = weekday - d.weekday()
        if next_days <= 0:
            next_days += 7
        return d + timedelta(days=next_days)


class Assistant:
    def __init__(self, book: AddressBook):
        self.book = book
        self.commands = {
            "hello": self.say_hello,
            "add": self.add_contact,
            "change": self.change_contact,
            "phone": self.show_phone,
            "all": self.show_all,
            "add-birthday": self.add_birthday,
            "show-birthday": self.show_birthday,
            "birthdays": self.show_birthdays,
            "close or exit": "",
            "help": self.show_help
        }
    @input_error
    def say_hello(self):
        print("How can I help you?")

    @input_error
    def add_contact(self, *args):
        name, phone, *_ = args
        record = self.book.find(name)
        message = "Contact updated."
        if record is None:
            record = Record(name)
            self.book.add_record(record)
            message = "Contact added."
        if phone:
            record.add_phone(phone)
        print(message)

    @input_error
    def change_contact(self, *args):
        name, new_phone, *_ = args
        record = self.book.find(name)
        if record:
            if new_phone:
                record.edit_phone(record.phones[0].value, new_phone)
                print("Contact updated.")
            else:
                raise ValueError("Enter the new phone number")
        else:
            raise KeyError("Enter correct user name")

    @input_error
    def show_phone(self, *args):
        name = args[0]
        record = self.book.find(name)
        if record:
            print(f"{name}`s phone {record.phones[0]}")
        else:
            print("Contact not found.")

    @input_error
    def show_all(self):
        for record in self.book.data.values():
            print(record)

    @input_error
    def add_birthday(self, *args):
        name, *_, birthday = args
        record = self.book.find(name)
        message = "Birthday added."
        if record is None:
            message = "Contact not found."
        if record:
            record.add_birthday(birthday)
        print(message)

    @input_error
    def show_birthday(self, *args):
        name = args[0]
        record = self.book.find(name)
        if record:
            print(f"{name}`s birthday {record.birthday}")
        else:
            print("Contact not found.")

    @input_error
    def show_birthdays(self, *args):
        get_upcoming_birthdays = self.book.get_upcoming_birthdays()
        if get_upcoming_birthdays:
            for birthday_info in get_upcoming_birthdays:
                print(f"{birthday_info['name']}'s birthday on {birthday_info['congratulation_date']}")
        else:
            print("No upcoming birthdays")

    @input_error
    def show_help(self):
        print("Available commands:")
        for command in self.commands.keys():
            print(command)


class AssistantForCustomer:
    def __init__(self):
        self.book = load_data()
        self.assistant = Assistant(book=self.book)


    def run(self):
        print("Welcome to the assistant bot!")
        while True:
            user_input = input("Enter a command: ")
            command, *args = user_input.split()
            command = command.lower()
            if command == "close" or command == "exit":
                print("Goodbye!")
                break
            elif command in self.assistant.commands:
                try:
                    self.assistant.commands[command](*args)
                except (ValueError, KeyError) as e:
                    print(e)
            else:
                print("Invalid command. Type 'help' for available commands.")

        save_data(self.book)


if __name__ == "__main__":
    bot = Assistant(book=AddressBook)
    go_assistant = AssistantForCustomer()
    go_assistant.run()