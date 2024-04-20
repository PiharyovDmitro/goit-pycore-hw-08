from collections import  UserDict
from datetime import datetime

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError("Invalid phone number.")
        
class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
             raise ValueError('Invalid date format. Use MM.DD.YYYY')
        
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_number(self, phone_number):
        self.phones = [p for p in self.phones if str(p) != phone_number]

    def edit_phone(self, value):
        pass

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)


    def __str__(self):
        return f"Contact name : {self.name.value}, phones: {';'.join(p.value for p in self.phones)}"
    
class AddressBook(UserDict):
    
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
         if name in self.data:
             del self.data[name]
         else:
            raise KeyError("Contact not found.")

    def find_next_birthday(self, weekday):
        today = datetime.now().date()
        next_birthday = None
        for record in self.data.values():
            if hasattr(record, 'birthday'):
                birthday = record.birthday.date.replace(year=today.year)
                if birthday < today:
                    birthday = birthday.replace(year=today.year + 1)
                if next_birthday is None or birthday < next_birthday:
                    next_birthday = birthday

        if next_birthday is not None:
            days_until_next_birthday = (next_birthday - today).days
            if days_until_next_birthday % 7 == weekday:
                return next_birthday
        return None

    def get_upcoming_birthday(self, days=7):
        today = datetime.now().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if hasattr(record, 'birthday'):
                birthday = record.birthday.date.replace(year=today.year)
                if birthday < today:
                    birthday = birthday.replace(year=today.year + 1)
                days_until_birthday = (birthday - today).days
                if 0 < days_until_birthday <= days:
                    upcoming_birthdays.append((record.name.value, birthday))

        return upcoming_birthdays


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            return str(ve)
        except IndexError:
            return "Enter user name."
        except KeyError:
            return "Contact not found."
    return wrapper


@input_error
def add_contact(args, book : AddressBook):
    name , phone, *_ = args
    record = book.find(name)
    massage = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        massage = "Contact added."
    if phone:
        record.add_phone(phone)
    return massage

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    
    for phone in record.phones:
        if str(phone) == old_phone:
            phone.value = new_phone
            return "Contact updated."
    
    raise ValueError("Phone number not found for this contact.")

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    return "; ".join(str(phone) for phone in record.phones)


@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    if hasattr(record, 'birthday'):
        return str(record.birthday.date)
    else:
        return "Birthday not found for this contact."

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthday()
    if upcoming_birthdays:
        return "\n".join(f"{name}: {date}" for name, date in upcoming_birthdays)
    else:
        return "No upcoming birthdays."


def parse_input(user_input):
    parts = user_input.strip().split(maxsplit=1)
    command = parts[0]
    args = parts[1].split() if len(parts) > 1 else [] 
    return command, *args

def main():
    book = AddressBook()
    print('''Welcome to the assistant bot!
          - close, exit: Programm is closed
          - hello: Greet
          - add[Name] [Phone]: Add contact
          - change[Name] [Old Phone] [New Phone]: Change contact
          - phone[Name]: Show phone by name
          - all: Show all contacts
          - add-birthday[Name] [Date]: Add birthday by Name
          - show-birthday[Name]: Show birthday by Name
          - birthdays: Show upcoming birthdays ''')
    
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()