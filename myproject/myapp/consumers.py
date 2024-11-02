import json
from channels.generic.websocket import AsyncWebsocketConsumer

class Player:
    def __init__(self, ip, name, balance):
        self.ip = ip
        self.name = name
        self.balance = balance

    def to_dict(self):
        return {"ip": self.ip, "name": self.name, "balance": self.balance}

players = {}
players_all = {}

class PlayerPoolConsumer(AsyncWebsocketConsumer):
    
    #handle when player join
    async def connect(self):
        self.room_group_name = 'player_pool'
        self.ip = self.scope['client'][0]

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        if self.ip in players_all:
            player = players_all[self.ip]
        else:
            player = Player(self.ip, f"Player_{self.ip}", 15150000)
            players_all[self.ip] = player

        players[self.ip] = player

        await self.send_personal_info()
        await self.broadcast_player_list()

    async def disconnect(self, close_code):
        if self.ip in players:
            del players[self.ip]
            await self.broadcast_player_list()

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            #handle when receive message
            if message_type == 'update_name':
                await self.update_name(data.get('name'))
            elif message_type == 'request_money':
                await self.handle_money_request(data)
            elif message_type == 'send_money':
                await self.handle_money_send(data)
            else:
                await self.send_error("Unknown message type")
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON")
        except Exception as e:
            await self.send_error(str(e))

    async def update_name(self, new_name):
        if not new_name or not isinstance(new_name, str):
            await self.send_error("Invalid name")
            return

        if self.ip in players:
            players[self.ip].name = new_name
            players_all[self.ip].name = new_name
            await self.send_personal_info()
            await self.broadcast_player_list()
        
        await self.broadcast_updates()
            
    async def broadcast_updates(self):
        #broadcast to all players
        await self.broadcast_player_list()
        
        #broadcast to all players
        for player in players.values():
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_player',
                    'player': player.to_dict()
                }
            )
        
    async def broadcast_personal_info(self, event):
        await self.send(json.dumps({
            'type': 'broadcast_personal_info',
            'info': event['info']
        }))

    
    #handle when money recive 
    async def handle_money_request(self, data):
        
        #from json file get amount
        amount = data.get('amount')
        
        #from json file get list of targets 
        targets = data.get('targets', [])
        
        #uncomment to test of data correctly
        #print(data)
        
        #error handle 
        if not isinstance(amount, (int, float)) or amount <= 0 or not targets:
            await self.send_error("Invalid money request")
            return
        
        #get the user name that who sent the message 
        requester_name = data.get('whosent')
        requester = next((p for p in players.values() if p.name == requester_name), None)
        
        
        if not requester:
            await self.send_error("Requester not found")
            return
        
        
        #loop throught the player htat in the list of targets
        for target_name in targets:
            target = next((p for p in players.values() if p.name == target_name), None)
            if target:
                if target.balance >= amount:
                    target.balance -= amount
                    requester.balance += amount

                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'money_request',
                            'requester': requester_name,
                            'target': target_name,
                            'amount': amount
                        }
                    )
                
                # update player info
                    await self.broadcast_player_list()
                else:
                    await self.send_error(f"{target_name} has insufficient balance")
            else:
                await self.send_error(f"Target {target_name} not found")
                

        # update the send_personnal info
        if self.ip == requester.ip:
            await self.send_personal_info()

        await self.broadcast_updates()
        
    
    
    
    #handle the money change 
    async def handle_money_send(self, data):
        
        amount = data.get('amount')
        targets = data.get('targets', [])
        if not isinstance(amount, (int, float)) or amount <= 0 or not targets:
            await self.send_error("Invalid money send request")
            return

        sender = players.get(self.ip)
        if not sender:
            await self.send_error("Sender not found")
            return

        total_amount = amount * len(targets)
        if sender.balance < total_amount:
            await self.send_error("Insufficient balance")
            return

        sender.balance -= total_amount
        for target_name in targets:
            target = next((p for p in players.values() if p.name == target_name), None)
            if target:
                target.balance += amount

        #await self.send_personal_info()
        #await self.broadcast_player_list()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'money_sent',
                'sender': sender.name,
                'targets': targets,
                'amount': amount
            }
        )
        
        await self.broadcast_updates()

    async def send_personal_info(self):
        player = players.get(self.ip)
        if player:
            await self.send(json.dumps({
                'type': 'personal_info',
                'name': player.name,
                'balance': player.balance
            }))

    async def broadcast_player_list(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_player_list',
            }
        )

    async def send_player_list(self, event):
        player_list = [player.to_dict() for player in players.values()]
        await self.send(json.dumps({
            'type': 'player_list',
            'players': player_list
        }))

    async def money_request(self, event):
        await self.send(json.dumps(event))

    
    async def money_sent(self, event):
        await self.send(json.dumps(event))

    async def send_error(self, message):
        await self.send(json.dumps({
            'type': 'error',
            'message': message
        }))