import os
import json
import time
import base64
import hashlib
import random
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests
from colorama import Fore, Style, init

# Initialize colorama
init()

class UniquidAPIClient:
    def __init__(self):
        self.base_url = "https://api.uniquid.io/mainnet"  # Base URL for all endpoints
        self.endpoints = {
            'login': f"{self.base_url}/user/login",
            'profile': f"{self.base_url}/user/profile",
            'task_list': f"{self.base_url}/task/list",
            'task_check': f"{self.base_url}/task/check",
            'get_question': f"{self.base_url}/user/getQuestion",
            'submit_answer': f"{self.base_url}/user/answer"
        }
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
            "Content-Type": "application/json",
            "Origin": "https://miniapp.uniquid.io",
            "Referer": "https://miniapp.uniquid.io/",
            "Sec-Ch-Ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S918BE) AppleWebKit/601.33 (KHTML, like Gecko) Chrome/108.0.2613.17 Mobile Safari/601.33"
        }
        self.token_file = os.path.join(os.path.dirname(__file__), 'token.json')
        self.is_running = True

    def generate_tp(self, init_data: str = None) -> str:
        input_data = init_data or "a"
        return hashlib.md5(input_data.encode()).hexdigest()

    def log(self, msg: str, type: str = 'info') -> None:
        timestamp = datetime.now().strftime('%H:%M:%S')
        if type == 'success':
            print(f"[{timestamp}] [✓] {Fore.GREEN}{msg}{Style.RESET_ALL}")
        elif type == 'custom':
            print(f"[{timestamp}] [*] {Fore.MAGENTA}{msg}{Style.RESET_ALL}")
        elif type == 'error':
            print(f"[{timestamp}] [✗] {Fore.RED}{msg}{Style.RESET_ALL}")
        elif type == 'warning':
            print(f"[{timestamp}] [!] {Fore.YELLOW}{msg}{Style.RESET_ALL}")
        else:  # default info
            print(f"[{timestamp}] [ℹ] {Fore.BLUE}{msg}{Style.RESET_ALL}")

    async def countdown(self, seconds: int) -> None:
        for i in range(seconds, 0, -1):
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"\r[{timestamp}] [*] Menunggu {i} detik untuk melanjutkan...", end='')
            time.sleep(1)
        print("\r" + " " * 80 + "\r", end='')

    def is_expired(self, token: str) -> bool:
        if not token:
            return True
        
        try:
            header, payload, sign = token.split('.')
            decoded_payload = base64.b64decode(payload + '=' * (-len(payload) % 4))
            parsed_payload = json.loads(decoded_payload)
            now = int(datetime.now().timestamp())
            
            if 'exp' in parsed_payload:
                expiration_date = datetime.fromtimestamp(parsed_payload['exp'])
                self.log(f"Token kadaluarsa pada: {expiration_date.strftime('%Y-%m-%d %H:%M:%S')}", 'custom')
                
                is_expired = now > parsed_payload['exp']
                self.log(f"Token sudah kadaluarsa? {'Ya, Anda perlu token baru' if is_expired else 'Belum..lanjut'}", 'custom')
                
                return is_expired
                
            self.log("Token permanen tidak dapat membaca waktu kadaluarsa", 'warning')
            return False
        except Exception as error:
            self.log(f"Error saat memeriksa token: {str(error)}", 'error')
            return True

    def load_tokens(self) -> Dict:
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as error:
            self.log(f"Error saat membaca file token: {str(error)}", 'error')
            return {}

    def save_token(self, user_id: str, token: str, init_data: str) -> Optional[Dict]:
        try:
            tokens = self.load_tokens()
            tp = self.generate_tp(init_data)
            tokens[user_id] = {
                'token': token,
                'init_data': init_data,
                'tp': tp
            }
            with open(self.token_file, 'w') as f:
                json.dump(tokens, f, indent=2)
            self.log(f"Berhasil menyimpan token untuk user {user_id}", 'success')
            return {'token': token, 'tp': tp}
        except Exception as error:
            self.log(f"Error saat menyimpan token: {str(error)}", 'error')
            return None

    async def login(self, init_data: str) -> Dict:
        try:
            # Extract query parameters from init_data
            params = dict(param.split('=') for param in init_data.split('&'))
            rel = params.get('start_param', '')
            user_data = json.loads(requests.utils.unquote(params.get('user', '{}')))

            payload = {
                "initData": init_data,
                "rel": rel,
                "give": 0
            }

            response = requests.post(self.endpoints['login'], json=payload, headers=self.headers)
            if response.status_code == 201 and response.json()['code'] == 0:
                self.log(f"Berhasil login akun: {user_data.get('username', 'Unknown')}!", 'success')
                return {
                    'success': True,
                    'token': response.json()['data']['access_token'],
                    'is_new': response.json()['data']['is_new'],
                    'user_id': user_data.get('id')
                }
            else:
                raise Exception(response.json().get('msg', 'Error tidak diketahui saat login'))
        except Exception as error:
            self.log(f"Error login: {str(error)}", 'error')
            return {'success': False, 'error': str(error)}

    async def get_user_profile(self, user_id: str, token: str, tp: str) -> Optional[Dict]:
        if not token or not tp:
            self.log(f"Token atau tp tidak lengkap untuk user {user_id}", 'error')
            return None

        try:
            url = f"{self.endpoints['profile']}?m={tp}"
            response = requests.get(url, headers={**self.headers, "Authorization": f"Bearer {token}"})
            data = response.json()

            if data['code'] != 0:
                raise Exception(data.get('msg', 'Error tidak diketahui saat mengambil profile'))

            return data
        except Exception as error:
            self.log(f"Error saat mengambil profile: {str(error)}", 'error')
            return None

    async def get_task_list(self, user_id: str, token: str, tp: str) -> Optional[List]:
        if not token or not tp:
            self.log(f"Token atau tp tidak lengkap untuk user {user_id}", 'error')
            return None

        try:
            url = f"{self.endpoints['task_list']}?m={tp}"
            response = requests.get(url, headers={**self.headers, "Authorization": f"Bearer {token}"})
            data = response.json()

            if data['code'] != 0:
                raise Exception(data.get('msg', 'Error tidak diketahui saat mengambil daftar tugas'))

            return data['data']['list']
        except Exception as error:
            self.log(f"Error saat mengambil daftar tugas: {str(error)}", 'error')
            return None

    async def check_task(self, task_type: str, user_id: str, token: str, tp: str) -> bool:
        if not token or not tp:
            self.log(f"Token atau tp tidak lengkap untuk user {user_id}", 'error')
            return False

        try:
            url = f"{self.endpoints['task_check']}?m={tp}"
            payload = {'type': task_type}
            response = requests.post(url, json=payload, headers={**self.headers, "Authorization": f"Bearer {token}"})
            data = response.json()

            if data['code'] != 0:
                raise Exception(data.get('msg', 'Error tidak diketahui saat memeriksa tugas'))

            return True
        except Exception as error:
            self.log(f"Error saat memeriksa tugas {task_type}: {str(error)}", 'error')
            return False

    async def get_question(self, user_id: str, token: str, tp: str) -> Optional[Dict]:
        if not token or not tp:
            self.log(f"Token atau tp tidak lengkap untuk user {user_id}", 'error')
            return None

        try:
            url = f"{self.endpoints['get_question']}?m={tp}"
            response = requests.get(url, headers={**self.headers, "Authorization": f"Bearer {token}"})
            data = response.json()

            if data['code'] != 0:
                raise Exception(data.get('msg', 'Error tidak diketahui saat mengambil pertanyaan'))

            return data['data']['question']
        except Exception as error:
            self.log(f"Error saat mengambil pertanyaan: {str(error)}", 'error')
            return None

    async def submit_answer(self, user_id: str, token: str, tp: str, answer: int) -> Optional[Dict]:
        if not token or not tp:
            self.log(f"Token atau tp tidak lengkap untuk user {user_id}", 'error')
            return None

        try:
            url = f"{self.endpoints['submit_answer']}?m={tp}"
            payload = {'answer': answer}
            response = requests.post(url, json=payload, headers={**self.headers, "Authorization": f"Bearer {token}"})
            data = response.json()

            if data['code'] != 0:
                raise Exception(data.get('msg', 'Error tidak diketahui saat menjawab pertanyaan'))

            return data['data']
        except Exception as error:
            self.log(f"Error saat menjawab pertanyaan: {str(error)}", 'error')
            return None

    async def handle_quiz(self, user_id: str, token: str, tp: str, chances: int) -> None:
        if chances <= 0:
            self.log("Tidak ada kesempatan tersisa untuk menjawab pertanyaan", 'warning')
            return

        self.log(f"Mulai menjawab pertanyaan dengan {chances} kesempatan", 'custom')

        while chances > 0:
            question = await self.get_question(user_id, token, tp)
            if not question:
                self.log("Tidak dapat mengambil pertanyaan", 'error')
                break

            self.log(f"Pertanyaan: {question['question']}", 'info')
            self.log(f"Pilihan: {' | '.join(question['options'])}", 'info')

            random_answer = 0  # Selalu pilih jawaban pertama
            result = await self.submit_answer(user_id, token, tp, random_answer)

            if result:
                if result['correct'] == 1:
                    self.log(f"Jawaban benar.. mendapat {result['points']} Points", 'success')
                else:
                    self.log("Jawaban salah", 'error')
                chances -= 1
                self.log(f"Sisa {chances} kesempatan", 'custom')

                delay = random.randint(1000, 3000) / 1000
                time.sleep(delay)

    async def process_all_tasks(self, user_id: str, token: str, tp: str) -> None:
        if not token or not tp:
            self.log(f"Token atau tp tidak lengkap untuk user {user_id}", 'error')
            return

        try:
            task_list = await self.get_task_list(user_id, token, tp)
            if not task_list:
                self.log('Tidak dapat mengambil daftar tugas', 'error')
                return

            profile = await self.get_user_profile(user_id, token, tp)
            if not profile or 'data' not in profile:
                self.log('Tidak dapat mengambil informasi profile', 'error')
                return

            completed_tasks = [
                *profile['data'].get('dailyTaskList', []),
                *profile['data'].get('taskList', [])
            ]

            self.log(f"Telah menyelesaikan {len(completed_tasks)} tugas", 'info')
            self.log(f"Point: {profile['data']['point']} | Kesempatan: {profile['data']['chances']}", 'custom')

            for task in task_list:
                if task['type'] == 'ConnectOkx':
                    self.log("Melewati tugas ConnectOkx", 'warning')
                    continue

                if task['type'] in completed_tasks:
                    self.log(f"Tugas {task['type']} sudah selesai sebelumnya", 'warning')
                    continue

                self.log(f"Memproses tugas: {task['type']}", 'info')
                success = await self.check_task(task['type'], user_id, token, tp)
                
                if success:
                    self.log(f"Berhasil menyelesaikan tugas {task['type']} | Hadiah: {task['points']} Points {task['chances']} Kesempatan", 'success')
                    
                    delay = random.randint(1000, 3000) / 1000
                    time.sleep(delay)

            updated_profile = await self.get_user_profile(user_id, token, tp)
            if updated_profile and 'data' in updated_profile:
                self.log("=== Update setelah menyelesaikan tugas ===", 'custom')
                self.log(f"Point: {updated_profile['data']['point']} | Kesempatan: {updated_profile['data']['chances']}", 'custom')
                self.log(f"Peringkat: {updated_profile['data']['rank']} | Point Bulanan: {updated_profile['data']['monthPoint']}", 'custom')

                if updated_profile['data']['chances'] > 0:
                    await self.handle_quiz(user_id, token, tp, updated_profile['data']['chances'])

        except Exception as error:
            self.log(f"Error saat memproses tugas: {str(error)}", 'error')

    async def get_user_task_summary(self, user_id: str, token: str, tp: str) -> Optional[Dict]:
        profile = await self.get_user_profile(user_id, token, tp)
        if not profile or 'data' not in profile:
            return None

        return {
            'dailyTasks': profile['data'].get('dailyTaskList', []),
            'regularTasks': profile['data'].get('taskList', []),
            'stats': {
                'points': profile['data']['point'],
                'chances': profile['data']['chances'],
                'rank': profile['data']['rank'],
                'monthPoints': profile['data']['monthPoint'],
                'correct': profile['data']['correct'],
                'wrong': profile['data']['wrong']
            }
        }

    async def main(self):
        data_file = os.path.join(os.path.dirname(__file__), 'data.txt')
        with open(data_file, 'r', encoding='utf-8') as f:
            data = [line.strip() for line in f if line.strip()]

        tokens = self.load_tokens()
        while True:
            for i, init_data in enumerate(data):
                user_data = json.loads(requests.utils.unquote(init_data.split('user=')[1].split('&')[0]))
                user_id = user_data['id']

                print(f"========== Akun {i + 1} | {Fore.GREEN}{user_data['first_name']}{Style.RESET_ALL} ==========")
                
                current_token = tokens.get(user_id, {}).get('token')
                current_tp = tokens.get(user_id, {}).get('tp')
                need_new_token = True

                if current_token:
                    self.log('Memeriksa token...', 'info')
                    if not self.is_expired(current_token):
                        self.log('Token masih aktif, melanjutkan penggunaan', 'success')
                        need_new_token = False
                    else:
                        self.log('Token sudah kadaluarsa, melakukan login ulang', 'warning')
                else:
                    self.log('Token tidak ditemukan, melakukan login', 'info')

                if need_new_token:
                    login_result = await self.login(init_data)
                    if login_result['success']:
                        saved_data = self.save_token(login_result['user_id'], login_result['token'], init_data)
                        if saved_data:
                            current_token = saved_data['token']
                            current_tp = saved_data['tp']
                    else:
                        self.log(f"Login gagal: {login_result['error']}", 'error')
                        continue

                profile = await self.get_user_profile(user_id, current_token, current_tp)
                if profile and 'data' in profile:
                    point = profile['data']['point']
                    correct = profile['data']['correct']
                    wrong = profile['data']['wrong']
                    self.log(f"Point: {point} | Benar: {correct} | Salah: {wrong}", 'custom')

                await self.process_all_tasks(user_id, current_token, current_tp)

                await self.countdown(2)
            
            await self.countdown(3600)

if __name__ == "__main__":
    import asyncio
    
    client = UniquidAPIClient()
    try:
        asyncio.run(client.main())
    except Exception as err:
        client.log(str(err), 'error')
        exit(1)