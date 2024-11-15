import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

class User:
    def __init__(self, id, user_name, account, company_id, points=0):
        self.id = id
        self.user_name = user_name
        self.account = account
        self.company_id = company_id
        self.points = points  # 기본 포인트값을 0으로 설정

    def update_points(self, new_points):
        self.points = new_points


# 일반 사용자
class NormalUser(User):
    def __init__(self, id, user_name, account, company_id, points=0):
        super().__init__(id, user_name, account, company_id, points)


# 관리자
class AdminUser(User):
    def __init__(self, id, user_name, account, points=0):
        super().__init__(id, user_name, account, points)

    # 관리자 기능: 모든 사용자 정보 조회 가능
    def select_user_info(self, user, user_name=None, account=None, company_id=None, points=None):
        if user_name:
            user.user_name = user_name
        if account:
            user.account = account
        if company_id:
            user.company_id = company_id
        if points is not None:
            user.points = points

    def show_admin_menu(self, menu_frame, users):
        menu_frame.pack(pady=20)

        admin_label = tk.Label(menu_frame, text="관리자 메뉴")
        admin_label.grid(row=0, column=0, columnspan=3)

        show_all_users_button = tk.Button(menu_frame, text="모든 사용자 보기", command=lambda: self.show_all_users(users))
        show_all_users_button.grid(row=1, column=0, columnspan=3)

    def show_all_users(self, users):
        for user in users:
            print(f"ID: {user.id}, 이름: {user.user_name}, 계정: {user.account}")


class Company:
    def __init__(self, id, company_name, breakfast_start, breakfast_end, lunch_start, lunch_end, dinner_start,
                 dinner_end, point):
        self.id = id
        self.company_name = company_name
        self.breakfast_start = breakfast_start
        self.breakfast_end = breakfast_end
        self.lunch_start = lunch_start
        self.lunch_end = lunch_end
        self.dinner_start = dinner_start
        self.dinner_end = dinner_end
        self.point = point  # 회사별 포인트


class Restaurant:
    def __init__(self, id, res_name, breakfast_menu, lunch_menu, dinner_menu, breakfast_start, breakfast_end,
                 lunch_start, lunch_end, dinner_start, dinner_end):
        self.id = id
        self.res_name = res_name
        self.breakfast_menu = breakfast_menu
        self.lunch_menu = lunch_menu
        self.dinner_menu = dinner_menu
        self.breakfast_start = breakfast_start
        self.breakfast_end = breakfast_end
        self.lunch_start = lunch_start
        self.lunch_end = lunch_end
        self.dinner_start = dinner_start
        self.dinner_end = dinner_end


# MealTime 클래스 : 식사 시간 관련
class MealTime:
    def __init__(self, current_time: str, company: Company, restaurant: Restaurant):
        self.current_time = current_time
        self.company = company
        self.restaurant = restaurant

    def is_within_time(self, start_time, end_time):
        current_time_obj = datetime.strptime(self.current_time, "%H:%M")
        start_time_obj = datetime.strptime(start_time, "%H:%M")
        end_time_obj = datetime.strptime(end_time, "%H:%M")
        return start_time_obj <= current_time_obj <= end_time_obj

    def get_meal_time_str(self):
        if self.is_within_time(self.company.breakfast_start, self.company.breakfast_end):
            return "아침"
        elif self.is_within_time(self.company.lunch_start, self.company.lunch_end):
            return "점심"
        elif self.is_within_time(self.company.dinner_start, self.company.dinner_end):
            return "저녁"
        else:
            return "식사 시간 종료"

    def is_valid_meal_time_for_restaurant(self):
        if self.is_within_time(self.restaurant.breakfast_start, self.restaurant.breakfast_end):
            return True
        elif self.is_within_time(self.restaurant.lunch_start, self.restaurant.lunch_end):
            return True
        elif self.is_within_time(self.restaurant.dinner_start, self.restaurant.dinner_end):
            return True
        return False

    def get_current_meal(self):
        return datetime.now().strftime("%H:%M")


class DataLoader:
    @staticmethod
    def load_data(file_path='database.json'):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            companies = [Company(company['id'], company['company_name'], company['breakfast_start'],
                                 company['breakfast_end'], company['lunch_start'], company['lunch_end'],
                                 company['dinner_start'], company['dinner_end'], company['point'])
                         for company in data['companies']]
            admin = data['admin']
            users = [User(user['id'], user['user_name'], user['account'], user['company_id'])
                     for user in data['users']]
            restaurants = [Restaurant(res['id'], res['res_name'], res['breakfast_menu'], res['lunch_menu'],
                                      res['dinner_menu'], res['breakfast_start'], res['breakfast_end'],
                                      res['lunch_start'], res['lunch_end'], res['dinner_start'], res['dinner_end'])
                           for res in data['restaurants']]
            return companies, admin, users, restaurants


class MainService:
    def __init__(self, master):
        self.master = master
        self.master.title("식권대장")
        self.master.geometry("500x300")
        self.load_data()

        self.user = None
        self.is_admin = False

        self.login_frame = tk.Frame(master)
        self.login_frame.pack(pady=20)

        self.label = tk.Label(self.login_frame, text="계정 입력:")
        self.label.grid(row=0, column=0)

        self.account_entry = tk.Entry(self.login_frame)
        self.account_entry.grid(row=0, column=1)

        self.login_button = tk.Button(self.login_frame, text="로그인", command=self.login)
        self.login_button.grid(row=0, column=2)

        self.menu_frame = tk.Frame(master)

    def load_data(self):
        self.companies, self.admin, self.users, self.restaurants = DataLoader.load_data()

    def login(self):
        account = self.account_entry.get()
        for admin in self.admin:
            if admin['account'] == account:
                self.is_admin = True
                self.user = AdminUser(admin['id'], admin['admin_name'], admin['account'], 0)
                self.show_admin_menu()
                return

        for user in self.users:
            if user.account == account:
                self.user = NormalUser(user.id, user.user_name, user.account, user.company_id, user.points)
                self.show_user_menu()  # 일반 사용자 메뉴로 이동
                return
        messagebox.showerror("로그인 실패", "잘못된 계정입니다.")

    def show_user_menu(self):
        self.login_frame.pack_forget()
        self.menu_frame.pack(pady=20)

        company = next(company for company in self.companies if company.id == self.user.company_id)
        restaurant = next(restaurant for restaurant in self.restaurants)  # 사용자가 선택한 식당을 가져옴

        meal_time_checker = MealTime(datetime.now().strftime("%H:%M"), company,
                                     restaurant)  # get_current_meal을 MealTime 클래스에서 호출

        meal_time_str = meal_time_checker.get_meal_time_str()  # 아침/점심/저녁 확인
        self.update_welcome_message(meal_time_str)

        if not meal_time_checker.is_valid_meal_time_for_restaurant():
            messagebox.showinfo("알림", "현재 영업 중인 식당이 없습니다.")
            return
    def show_admin_menu(self):
        self.login_frame.pack_forget()
        self.menu_frame.pack(pady=20)

        admin = AdminUser(self.user.id, self.user.user_name, self.user.account)  # AdminUser 객체 생성
        admin.show_admin_menu(self.menu_frame, self.users)  # 관리자 메뉴 호출

    def update_welcome_message(self, meal_time_str):
        welcome_message = "{}님\n현재 포인트: {}원\n회사 현재 : {}".format(self.user.user_name, self.user.points, meal_time_str)
        if hasattr(self, 'welcome_label'):
            self.welcome_label.config(text=welcome_message)
        else:
            self.welcome_label = tk.Label(self.menu_frame, text=welcome_message)
            self.welcome_label.grid(row=0, column=0, columnspan=3)

    def show_all_users(self):
        for user in self.users:
            print(f"ID: {user.id}, 이름: {user.user_name}, 계정: {user.account}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainService(root)
    root.mainloop()
