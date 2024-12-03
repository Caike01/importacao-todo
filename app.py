import flet as ft
import sqlite3
import os

class ToDo:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.bgcolor = ft.colors.WHITE
        self.page.window_width = 350
        self.page.window_height = 450
        self.page.window_resizable = False
        self.page.window_always_on_top = True
        self.page.title = 'ToDo APP'
        self.task = ''
        self.view = 'all'
        self.db_execute('CREATE TABLE IF NOT EXISTS tasks(name TEXT, status TEXT)')
        self.results = self.db_execute('SELECT * FROM tasks')
        self.main_page()

    def db_execute(self, query, params=[]):
        # Usando o banco de dados do diretório atual
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute(query, params)
            con.commit()
            return cur.fetchall()

    def checked(self, e):
        is_checked = e.control.value
        label = e.control.label

        # Atualizando o status da tarefa no banco de dados
        if is_checked:
            self.db_execute('UPDATE tasks SET status = "complete" WHERE name = ?', params=[label])
        else:
            self.db_execute('UPDATE tasks SET status = "incomplete" WHERE name = ?', params=[label])

        # Filtrando as tarefas de acordo com a visão selecionada (todos, incompletos ou completos)
        if self.view == 'all':
            self.results = self.db_execute('SELECT * FROM tasks')
        else:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = ?', params=[self.view])

        self.update_task_list()

    def tasks_container(self):
        # Criando o container com a lista de tarefas
        return ft.Container(
            height=self.page.height * 0.8,
            content=ft.Column(
                controls=[
                    ft.Checkbox(label=res[0],
                                on_change=self.checked,
                                value=True if res[1] == 'complete' else False)
                    for res in self.results if res
                ],
            )
        )

    def set_value(self, e):
        # Atualizando o valor da tarefa
        self.task = e.control.value

    def add(self, e, input_task):
        name = self.task
        status = 'incomplete'

        # Adicionando uma nova tarefa no banco de dados
        if name:
            self.db_execute(query='INSERT INTO tasks values(?, ?)', params=[name, status])
            input_task.value = ''
            self.results = self.db_execute('SELECT * FROM tasks')
            self.update_task_list()

    def update_task_list(self):
        # Atualizando a lista de tarefas na interface
        tasks = self.tasks_container()
        self.page.controls.pop()
        self.page.add(tasks)
        self.page.update()

    def tabs_changed(self, e):
        # Atualizando a visão de acordo com a tab selecionada
        if e.control.selected_index == 0:
            self.results = self.db_execute('SELECT * FROM tasks')
            self.view = 'all'
        elif e.control.selected_index == 1:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = "incomplete"')
            self.view = 'incomplete'
        elif e.control.selected_index == 2:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = "complete"')
            self.view = 'complete'

        self.update_task_list()

    def main_page(self):
        # Campo de input para digitar tarefas
        input_task = ft.TextField(
            hint_text='Digite uma tarefa',
            expand=True,
            on_change=self.set_value
        )

        input_bar = ft.Row(
            controls=[
                input_task,
                ft.FloatingActionButton(
                    icon=ft.icons.ADD,
                    on_click=lambda e: self.add(e, input_task)
                )
            ]
        )

        tabs = ft.Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[
                ft.Tab(text='Todos'),
                ft.Tab(text='Em andamento'),
                ft.Tab(text='Finalizados')
            ]
        )

        tasks = self.tasks_container()

        self.page.add(input_bar, tabs, tasks)

ft.app(target=ToDo)
