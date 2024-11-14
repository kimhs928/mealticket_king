import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime


class Restaurant:
    def __init__(self, id, res_name, breakfast_menu, lunch_menu, dinner_menu, breakfast_start, breakfast_end, lunch_start, lunch_end, dinner_start, dinner_end):
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


class User:
    def __init__(self, id, user_name, account, company_id, points=0):
        self.id = id
        self.user_name = user_name
        self.account = account
        self.company_id = company_id
        self.points = points  # 기본 포인트값을 0으로 설정


class Company:
    def __init__(self, id, company_name, breakfast_start, breakfast_end, lunch_start, lunch_end, dinner_start, dinner_end, point):
        self.id = id
        self.company_name = company_name
        self.breakfast_start = breakfast_start
        self.breakfast_end = breakfast_end
        self.lunch_start = lunch_start
        self.lunch_end = lunch_end
        self.dinner_start = dinner_start
        self.dinner_end = dinner_end
        self.point = point  # 회사별 포인트


class App:
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
        with open('database.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.companies = [Company(company['id'], company['company_name'], company['breakfast_start'],
                                      company['breakfast_end'], company['lunch_start'], company['lunch_end'],
                                      company['dinner_start'], company['dinner_end'], company['point'])
                              for company in data['companies']]
            self.admin = data['admin']
            self.users = [User(user['id'], user['user_name'], user['account'], user['company_id'])
                          for user in data['users']]
            self.restaurants = [
                Restaurant(res['id'], res['res_name'], res['breakfast_menu'], res['lunch_menu'],
                           res['dinner_menu'], res['breakfast_start'], res['breakfast_end'],
                           res['lunch_start'], res['lunch_end'], res['dinner_start'], res['dinner_end'])
                for res in data['restaurants']
            ]

    def login(self):
        account = self.account_entry.get()
        if account == "aaa@@":
            self.is_admin = True
            self.show_admin_menu()
            return

        for user in self.users:
            if user.account == account:
                self.user = user
                self.show_user_menu()
                return
        messagebox.showerror("로그인 실패", "잘못된 계정입니다.")

    def show_user_menu(self):
        self.login_frame.pack_forget()
        self.menu_frame.pack(pady=20)

        company = next(company for company in self.companies if company.id == self.user.company_id)

        current_time = self.get_current_meal()
        meal_time_str = self.get_meal_time_str(current_time, company)

        # 회사에 맞는 포인트 갱신
        self.update_points_based_on_time(company, current_time)

        self.update_welcome_message(meal_time_str)

        # 영업시간에 맞는 식당을 가져옴
        valid_restaurants = self.get_valid_restaurants(current_time)

        if not valid_restaurants:  # 식당이 영업 중이지 않으면 오류 메시지 표시
            messagebox.showinfo("알림", "현재 영업 중인 식당이 없습니다.")
            return

        self.restaurant_label = tk.Label(self.menu_frame, text="식당 선택:")
        self.restaurant_label.grid(row=1, column=0)

        self.restaurant_var = tk.StringVar(self.menu_frame)
        self.restaurant_var.set("식당 선택")  # 초기값 설정

        self.restaurant_menu = tk.OptionMenu(self.menu_frame,
                                             self.restaurant_var,
                                             *valid_restaurants)
        self.restaurant_menu.grid(row=1, column=1)

        self.select_button = tk.Button(self.menu_frame, text="메뉴 보기", command=self.show_selected_menu)
        self.select_button.grid(row=1, column=2)

    def update_welcome_message(self, meal_time_str):
        welcome_message = "{}님\n현재 포인트: {}원\n현재 : {}".format(self.user.user_name, self.user.points, meal_time_str)
        if hasattr(self, 'welcome_label'):
            self.welcome_label.config(text=welcome_message)
        else:
            self.welcome_label = tk.Label(self.menu_frame, text=welcome_message)
            self.welcome_label.grid(row=0, column=0, columnspan=3)

    def get_current_meal(self):
        return datetime.now().strftime("%H:%M")

    def get_meal_time_str(self, current_time, company):
        if self.is_within_time(current_time, company.breakfast_start, company.breakfast_end):
            return "아침"
        elif self.is_within_time(current_time, company.lunch_start, company.lunch_end):
            return "점심"
        elif self.is_within_time(current_time, company.dinner_start, company.dinner_end):
            return "저녁"
        else:
            return "식사 시간 종료"

    def is_within_time(self, current_time, start_time, end_time):
        """시간을 datetime 객체로 변환하여 비교"""
        # If current_time is already a datetime object, no need to convert
        if isinstance(current_time, str):
            current_time_obj = datetime.strptime(current_time, "%H:%M")
        else:
            current_time_obj = current_time  # If it's already a datetime object, use it directly

        # Convert start_time and end_time to datetime objects for comparison
        start_time_obj = datetime.strptime(start_time, "%H:%M")
        end_time_obj = datetime.strptime(end_time, "%H:%M")

        return start_time_obj <= current_time_obj <= end_time_obj

    def update_points_based_on_time(self, company, current_time):
        if self.is_within_time(current_time, company.breakfast_start, company.breakfast_end):
            self.user.points = company.point
        elif self.is_within_time(current_time, company.lunch_start, company.lunch_end):
            self.user.points = company.point
        elif self.is_within_time(current_time, company.dinner_start, company.dinner_end):
            self.user.points = company.point
        else:
            self.user.points = 0  # 식사시간이 아니면 포인트 0으로 초기화

        # 업데이트된 포인트를 json에 반영
        self.update_user_points_in_json()

    def update_user_points_in_json(self):
        for user in self.users:
            if user.id == self.user.id:
                user.points = self.user.points  # 사용자 포인트 업데이트
                break

        with open('database.json', 'w', encoding='utf-8') as file:
            data = {
                'companies': [company.__dict__ for company in self.companies],
                'admin': self.admin,
                'users': [user.__dict__ for user in self.users],
                'restaurants': [restaurant.__dict__ for restaurant in self.restaurants],
            }
            json.dump(data, file, ensure_ascii=False, indent=4)

    def get_valid_restaurants(self, current_time):
        valid_restaurants = []
        current_time_obj = datetime.strptime(current_time, "%H:%M")  # current_time을 datetime 객체로 변환

        for restaurant in self.restaurants:
            # 식당의 영업 시간과 현재 시간이 맞는지 비교
            if self.is_within_time(current_time_obj, restaurant.breakfast_start, restaurant.breakfast_end):
                valid_restaurants.append(restaurant.res_name)
            elif self.is_within_time(current_time_obj, restaurant.lunch_start, restaurant.lunch_end):
                valid_restaurants.append(restaurant.res_name)
            elif self.is_within_time(current_time_obj, restaurant.dinner_start, restaurant.dinner_end):
                valid_restaurants.append(restaurant.res_name)

        return valid_restaurants

    def show_selected_menu(self):
        selected_res_name = self.restaurant_var.get()
        for restaurant in self.restaurants:
            if restaurant.res_name == selected_res_name:
                company = next(company for company in self.companies if company.id == self.user.company_id)
                current_time = self.get_current_meal()
                menu_message = "식당: {}\n".format(restaurant.res_name)

                menu = []
                if self.is_within_time(current_time, company.breakfast_start, company.breakfast_end) and restaurant.breakfast_menu:
                    menu_message += "아침 메뉴:\n"
                    menu = restaurant.breakfast_menu
                elif self.is_within_time(current_time, company.lunch_start, company.lunch_end) and restaurant.lunch_menu:
                    menu_message += "점심 메뉴:\n"
                    menu = restaurant.lunch_menu
                elif self.is_within_time(current_time, company.dinner_start, company.dinner_end) and restaurant.dinner_menu:
                    menu_message += "저녁 메뉴:\n"
                    menu = restaurant.dinner_menu

                if menu:  # 메뉴가 있을 경우
                    for item in menu:
                        menu_message += "{} - {}원\n".format(item['name'], item['price'])

                    self.create_menu_buttons(menu)
                else:
                    price_input = simpledialog.askinteger("금액 입력", "직접 금액을 입력하세요:")  # 금액 입력 받기
                    if price_input is not None:
                        self.process_payment(price_input)

                return

    def create_menu_buttons(self, menu):
        for widget in self.menu_frame.winfo_children():
            widget.grid_forget()

        self.restaurant_label.grid(row=1, column=0)
        self.restaurant_menu.grid(row=1, column=1)
        self.select_button.grid(row=1, column=2)

        for idx, item in enumerate(menu):
            button = tk.Button(self.menu_frame, text="{} - {}원".format(item['name'], item['price']),
                               command=lambda item=item: self.process_payment(item['price']))
            button.grid(row=2 + idx, column=0, columnspan=3)

    def process_payment(self, amount):
        if self.user.points >= amount:
            self.user.points -= amount
            messagebox.showinfo("결제 성공", "{}원 차감. 남은 포인트: {}원".format(amount, self.user.points))
            self.update_welcome_message(meal_time_str="")  # 결제 후 사용자 포인트 업데이트
        else:
            messagebox.showerror("결제 실패", "포인트 부족.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
