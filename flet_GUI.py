import flet as ft
import file_crypto_upload as cfu
import alist as at


def main(page: ft.Page):
    page.title = "Quantum Encryption Network Drive"
    page.window_bgcolor = ft.colors.TRANSPARENT
    page.bgcolor = "#FCE9DB"
    page.window_frameless = True
    page.window_width = 800
    page.window_height = 500
    page.window_min_width = 800
    page.window_min_height = 500
    page.auto_scroll = True
    page.scroll = "AUTO"
    page.window_center()
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.theme.Theme(
        color_scheme_seed='purple', font_family="YeZi")
    page.update()
    # 页面字体
    page.fonts = {
        "ZiYu": "font/ziyu.ttf",
        "Quantum": "font/Quantum-2.otf",
        "ColorTube": "font/ColorTube-2.otf",
        "YeZi": "font/YeZiGongChangAoYeHei-2.ttf"
    }
    page.vertical_alignment = ft.MainAxisAlignment.SPACE_AROUND  # 垂直居中
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER  # 水平居中

    # 登录按钮点击事件
    def btn_login_click(e):
        token = at.get_token(username_box.value, password_box.value)
        at.token = token
        user = at.get_user_info()
        if token == '400':
            print("Wrong Username or Password!")
            page.dialog = w_pwd_dlg
            w_pwd_dlg.open = True
            page.update()
        elif token == '429':
            print("Too Many Errors!")
            page.dialog = e_lg_dlg
            e_lg_dlg.open = True
            page.update()
        elif user == '401':
            print("User Disabled!")
            page.dialog = d_dlg
            d_dlg.open = True
            page.update()
        elif user['permission'] == 0:
            print("User Permission Denied!")
            page.dialog = p_dlg
            p_dlg.open = True
            page.update()
        else:
            print("Login success!")
            main_page(page)

    def main_page(page: ft.Page):
        page.clean()
        page.vertical_alignment = ft.MainAxisAlignment.START  # 垂直居中
        page.window_height = 600
        page.window_min_height = 600

        # 上传文件按钮事件 加密上传
        def upload_file_click(e):
            file_path = local_file_path.value
            prog = ft.ProgressBar(width=500, color="#B28BCA", bgcolor="#FCE9DB")
            prog_bar.content = prog
            prog_bar.update()
            if not cfu.upload_file(file_path):
                local_file_path.value = "Encryption and Upload Failed!"
                local_file_path.color = "#F3292A"
                local_file_path.update()
            else:
                local_file_path.value = "Encryption and Upload Successful!"
                local_file_path.color = "#34A853"
                local_file_path.update()
            prog_bar.content = None
            prog_bar.update()

        # 文件选择器
        def pick_files_result(e: ft.FilePickerResultEvent):
            # local_file_name.value = e.files[0].name
            local_file_path.value = e.files[0].path
            local_file_path.color = "black"
            # local_file_size.value = e.files[0].size
            # local_file_name.update()
            local_file_path.update()
            # local_file_size.update()
            page.update()

        pick_files_dialog = ft.FilePicker(on_result=pick_files_result)

        # 目录选择器
        def get_directory_result(e: ft.FilePickerResultEvent):
            if file_name_box.value == "":
                local_file_path.value = "Please select a file!"
                local_file_path.color = "#F3292A"
                local_file_path.update()
                return 0
            local_file_path.value = e.path if e.path else "Cancelled!"
            if local_file_path.value == "Cancelled!":
                local_file_path.color = "#F3292A"
                return 0
            local_file_path.color = "black"
            local_file_path.update()
            page.update()
            path = local_file_path.value
            file_name = file_name_box.value
            prog = ft.ProgressBar(width=500, color="#B28BCA", bgcolor="#FCE9DB")
            prog_bar.content = prog
            prog_bar.update()
            if not cfu.download_file(file_name, path):
                local_file_path.value = "Download and Decrypto Failed!"
                local_file_path.color = "#F3292A"
                local_file_path.update()
            else:
                local_file_path.value = "Download and Decrypto Successful!"
                local_file_path.color = "#34A853"
                local_file_path.update()
            prog_bar.content = None
            prog_bar.update()

        get_directory_dialog = ft.FilePicker(on_result=get_directory_result)

        # 隐藏所有弹窗
        page.overlay.extend([pick_files_dialog, get_directory_dialog])

        # 下载文件按钮 选择目录同时下载解密
        btn_download_file = ft.ElevatedButton(
            'Download and Decrypto File',
            icon=ft.icons.DOWNLOAD,
            on_click=lambda _: get_directory_dialog.get_directory_path(
                # initial_directory="C:\\",
                dialog_title="Select a Directory",
            ),
        )

        # 选择文件按钮
        btn_select_file = ft.ElevatedButton(
            "Select Files",
            icon=ft.icons.FILE_OPEN,
            on_click=lambda _: pick_files_dialog.pick_files(
                allow_multiple=False
            ),
        )

        # 上传文件按钮
        btn_upload_file = ft.ElevatedButton(
            'Encrypto and Upload File',
            icon=ft.icons.UPLOAD_FILE_SHARP,
            on_click=upload_file_click
        )

        # 单选框改变事件
        def radiogroup_changed(e):
            file_name_box.value = e.control.value
            file_name_box.update()

        # 单选框组
        radio_group = ft.RadioGroup(
            content=ft.Column(
                [],
                spacing=0,
                wrap=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            on_change=radiogroup_changed,
        )

        # 列出云端文件按钮事件
        def list_files_click(e):
            cloud_file_lists.controls.clear()
            cloud_file_lists.horizontal_alignment = ft.CrossAxisAlignment.START
            cloud_file_lists.alignment = ft.MainAxisAlignment.START
            file_lists = at.list_files()
            cloud_file_lists.clean()
            radio_group.content.controls.clear()
            if file_lists == 0:
                cloud_file_lists.controls.append(
                    ft.Text("No Files Found!", color="#F3292A")
                )
                cloud_file_lists.update()
                return 0
            for i, file in enumerate(file_lists):
                radio_group.content.controls.append(
                    ft.Radio(
                        value=file['name'],
                        label=f"{file['type']}  {file['name']}  <{file['size']}B>  ({file['time']})",
                    )
                )
            cloud_file_lists.controls.append(radio_group)
            cloud_file_lists.update()

        # 列出文件按钮
        btn_list_files = ft.ElevatedButton(
            "List Cloud Files",
            icon=ft.icons.LIST,
            on_click=list_files_click
        )

        # 输入文件名
        file_name_box = ft.TextField(
            label="File Name",
            hint_text="Select a File",
            width=230,
            height=45,
            max_lines=1,
            content_padding=5,
            text_size=14,
            border_radius=10
        )

        # 进度条容器
        prog_bar = ft.Container(
            width=600,
            height=5,
            alignment=ft.alignment.center,
            padding=0
        )

        # 选择文件信息展示
        # local_file_name = ft.Text()
        local_file_path = ft.Text("File or Directory Path")
        # local_file_size = ft.Text()

        # 云盘文件信息展示
        cloud_file_lists = ft.Column(
            height=180,
            width=650,
            spacing=0,
            scroll=ft.ScrollMode.HIDDEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text(at.check_server(),
                        color="#34A853",
                        ),
            ]
        )

        # logo和标题
        logo_image.width = 100
        title.controls[0].spans[0].text = "File Upload And Download"
        title.controls[1].spans[0].text = "File Upload And Download"
        page.add(ft.Column(
            [
                ft.Row(
                    [
                        logo_image,
                        title,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        btn_select_file,
                        btn_upload_file,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        # local_file_name,
                        local_file_path,
                        # local_file_size,prog_bar,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        prog_bar,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        btn_list_files,
                        file_name_box,
                        btn_download_file,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        cloud_file_lists
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=30,
        ))
        page.update()

    # 错误弹窗
    w_pwd_dlg = ft.AlertDialog(
        title=ft.Text(
            "Wrong Username or Password!\n\nPlease check your username and password!"),
    )
    e_lg_dlg = ft.AlertDialog(
        title=ft.Text(
            "Too Many Errors!\n\nPlease try again later in a few minutes!"),
    )
    d_dlg = ft.AlertDialog(
        title=ft.Text(
            "This user has been disabled!"
        )
    )
    p_dlg = ft.AlertDialog(
        title=ft.Text(
            "This user does not have permission!"
        )
    )


    title = ft.Stack(
        [
            ft.Text(
                spans=[
                    ft.TextSpan(
                        "Quantum Encryption Network Drive",
                        ft.TextStyle(
                            size=40,
                            weight=ft.FontWeight.BOLD,
                            foreground=ft.Paint(
                                color="#BF7BCA",
                                stroke_width=6,
                                stroke_join=ft.StrokeJoin.ROUND,
                                style=ft.PaintingStyle.STROKE,
                            ),
                        ),
                    ),
                ],
            ),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        "Quantum Encryption Network Drive",
                        ft.TextStyle(
                            size=40,
                            weight=ft.FontWeight.BOLD,
                            color="#FCE9DB",
                        ),
                    ),
                ],
            ),
        ]
    )
    logo_image = ft.Image(
        src="image/cloud-drive.png",
        width=200,
    )
    page.add(title)
    page.add(logo_image)
    password_box = ft.TextField(
        label="Password",
        hint_text="Please enter your password",
        max_lines=1,
        width=350,
        height=55,
        password=True,
        can_reveal_password=True,
        keyboard_type=ft.KeyboardType.VISIBLE_PASSWORD,
        shift_enter=True,
        on_submit=btn_login_click
    )
    username_box = ft.TextField(
        label="Username",
        hint_text="Please enter your username",
        max_lines=1,
        width=350,
        height=55,
        autofocus=True,
        shift_enter=True,
        on_submit=lambda e: password_box.focus(),
    )

    btn_login = ft.ElevatedButton(
        text="Login",
        width=200,
        height=50,
        animate_size=True,
        on_click=btn_login_click,
        icon=ft.icons.LOGIN,
    )
    # 登录框和按钮
    page.add(ft.Column(
        [
            ft.Row(
                [
                    # ft.Text("Username:"),
                    username_box
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    # ft.Text("Password:"),
                    password_box
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    btn_login
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        # 居中
        spacing=20,
    ))

    page.padding = 20  # 设置内边距
    page.update()


ft.app(target=main, assets_dir="asset")
