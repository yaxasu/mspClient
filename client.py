#-----------------------------------------------------------------------------------------
# 
# MAIN MSP CLIENT
#
#-----------------------------------------------------------------------------------------

import json
import websocket
import requests
from msp import invoke_method, get_session_id, ticket_header
from datetime import datetime
import requests
import data_pb2
from google.protobuf.json_format import MessageToJson
import re

#-----------------------------------------------------------------------------------------
# Needs to be built out by adding more functions/features
#-----------------------------------------------------------------------------------------
class MSPClient:
    def __init__(self, server, actor_id, name, ticket, access_token, profile_id, culture):
        self.server = server
        self.actor_id = actor_id
        self.name = name
        self.ticket = ticket
        self.access_token = access_token
        self.profile_id = profile_id
        self.culture = culture
        self.ws = None
        
    def establish_websocket_connection(self):
        """Establish a WebSocket connection to the server."""
        address = "https://presence-us.mspapis.com/getServer" if self.server == "us" else "https://presence.mspapis.com/getServer"
        formatted_address = requests.get(address).text.replace('-', '.')
        formatted_url = f"ws://{formatted_address}:10843/{formatted_address.replace('.', '-')}/?transport=websocket"
        
        self.ws = websocket.WebSocket()
        self.ws.connect(formatted_url)
        print("WebSocket connection established.")

        message_payload = json.dumps([
            "10", {
                "messageType": 10,
                "messageContent": {
                    "version": 3,
                    "applicationId": "APPLICATION_WEB",
                    "country": self.server,
                    "username": self.profile_id,
                    "access_token": self.access_token
                }
            }
        ])
        self.ws.send(f"42{message_payload}")
        print("Message sent.")

    def close_connection(self):
        """Close the WebSocket connection."""
        if self.ws:
            self.ws.close()
            print("WebSocket connection closed.")
        else:
            print("No WebSocket connection to close.")

    @staticmethod
    def user_login(server, username, password):
        """Login to the MSP server and retrieve user information."""
        code, resp = invoke_method(
            server,
            "MovieStarPlanet.WebService.User.AMFUserServiceWeb.Login",
            [
                username,
                password,
                [],
                None,
                None,
                "MSP1-Standalone:XXXXXX"
            ],
            get_session_id()
        )

        status = resp['loginStatus']['status']
        if status != "Success":
            print(f"Login failed, status: {status}")
            quit()

        actor_id = resp['loginStatus']['actor']['ActorId']
        name = resp['loginStatus']['actor']['Name']
        ticket = resp['loginStatus']['ticket']
        access_token = resp['loginStatus']['nebulaLoginStatus']['accessToken']
        profile_id = resp['loginStatus']['nebulaLoginStatus']['profileId']
        culture = resp['loginStatus']['actorLocale'][0]

        return [actor_id, name, ticket, access_token, profile_id, culture]

    def get_actor_id_from_user(self, user):
        """Get the ActorId from the username."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.GetActorIdFromName",
            [user],
            get_session_id()
        )
        return resp
    
    def msp_query(self, friend_actor_id):
        """Query for user details."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.AMFActorService.BulkLoadActors",
            [
                ticket_header(self.ticket),
                [friend_actor_id]
            ],
            get_session_id()
        )
        return [resp[0]['Money'], resp[0]["Diamonds"], resp[0]["Fame"]]

    def send_autograph(self, friend_actor_id):
        """Send an autograph to a friend."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.GiveAutographAndCalculateTimestamp",
            [
                ticket_header(self.ticket),
                self.actor_id,
                friend_actor_id
            ],
            get_session_id()
        )
        return resp
    
    def get_movie_id_from_actor_id(self, friend_actor):
        """Get MovieId from ActorId."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.MovieService.AMFMovieService.GetMovieListForActor",
            [
                ticket_header(self.ticket),
                friend_actor,
                2,
                0,
                16
            ],
            get_session_id()
        )
        return resp["list"][0]["movieId"]
    
    def get_movie(self, movie_id):
        """Retrieve a movie by its ID."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.MovieService.AMFMovieService.GetMovieById",
            [
                ticket_header(self.ticket),
                movie_id,
            ],
            get_session_id()
        )
        return resp
    
    def watch_movie(self, movie_id):
        """Mark a movie as watched."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.MovieService.AMFMovieService.MovieWatched",
            [
                ticket_header(self.ticket),
                movie_id,
                self.actor_id
            ],
            get_session_id()
        )
        return resp

    def view_gift(self):
        """View the latest gift."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Gifts.AMFGiftsService+Version2.GetGiftsNewPaged",
            [
                ticket_header(self.ticket),
                self.actor_id,
                0,
                6
            ],
            get_session_id()
        )
        gift_id = resp['Items'][0]['GiftId']
        return int(gift_id)
    
    def open_gift(self, gift_id):
        """Open a gift."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Gifts.AMFGiftsService+Version2.OpenGift",
            [
                ticket_header(self.ticket),
                self.actor_id,
                gift_id
            ],
            get_session_id()
        )
        return resp

    def send_gift(self, friend_actor, gift_id):
        """Send a gift to a friend."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Gifts.AMFGiftsService+Version2.GiveGiftOfCategory",
            [
                ticket_header(self.ticket),
                self.actor_id,
                friend_actor,
                gift_id,
                0,
                1,
                "Gift_item_3.swf"
            ],
            get_session_id()
        )
        print(resp)

    def validate_bot(self):
        """Validate the bot by claiming a daily award."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Awarding.AMFAwardingService.claimDailyAward",
            [
                ticket_header(self.ticket),
                "wheel",
                120,
                self.actor_id
            ],
            get_session_id()
        )
        print(resp)

    def feed_bonster(self, bonster_id):
        """Feed a bonster."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Bonster.AMFBonsterService.FeedBonster",
            [
                ticket_header(self.ticket),
                bonster_id,
                6,
                self.actor_id
            ],
            get_session_id()
        )
        print(resp)

    def wash_bonster(self, bonster_id):
        """Wash a bonster."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Bonster.AMFBonsterService.WashBonster",
            [
                ticket_header(self.ticket),
                bonster_id,
                100,
                self.actor_id
            ],
            get_session_id()
        )
        print(resp)
    
    def play_with_bonster(self, bonster_id):
        """Play with a bonster."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Bonster.AMFBonsterService.PlayWithBonster",
            [
                ticket_header(self.ticket),
                bonster_id,
                100,
                self.actor_id
            ],
            get_session_id()
        )
        print(resp)

    def buy_fame_booster(self):
        """Buy a fame booster."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Spending.AMFSpendingService.BuyFameBooster",
            [
                ticket_header(self.ticket),
                self.actor_id
            ],
            get_session_id()
        )
        return resp
    
    def captcha_v3():
        """Generate a valid captcha string"""
        try:
            url = "https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LcxuOsUAAAAAI2IYDfxOvAZrwRg2T1E7sJq96eg&co=aHR0cHM6Ly93d3cubW92aWVzdGFycGxhbmV0LmNvbTo0NDM.&hl=fr&v=vP4jQKq0YJFzU6e21-BGy3GP&size=invisible&cb=oul7f799qkr6"
            response = requests.get(url).text

            proto_data = data_pb2.ProtobufData(
                A="qljbK_DTcvY1PzbR7IG69z1r",
                    B=re.search(r'value="([^"]*)"', response).group(1),
                    C="!7Oqg6u8KAAQeF6g9bQEHDwLHaMPdyY7ouljPgQLRkFk2F1_itEwRVMtNNtAClz4c9AJDkWZ0NDXld44MdB1GiLK3E3ykbGIqxFYsRce3-5wFxCJ8MDLUgEO21E4ZdXE05UJAytb9NZWAzdh9D0hVUfS1xCqJ5LGAEuAqvx6GwI76CT8bWF2EAtnEIeuK7YdFYVMCMfkwroua67Hs0vQXjCp3aC9aOL1dsjdH5QG5FjvX7bUyFWxm0du9GvS-O4ZD5ABvfNxd4GW9GfPWlSy2TKIx0eaPPvb4cGxFwHSbDpCvkENiej4PZw8d4oXCitcFzK2QbmbV5WlikvzC2GRRhyIYC2FNm1leYH1ZzwHBRXim1YA0JswO2-lBZ-Hk3Fo-q1LL6ZAIM3FoMwk5ZIUUhhady-Mp4HfP3ZW4vaZELKq6tbH0cNt-LXItIv7obnR5g865bfiI3ghOuJMPlEbdZBt5RG5j1gSoTMaOIgKXDjBrHfLdaK-L9uz6P6RegHy9aaTFWOJF092IwxB_7fdLqQtbOWYCmPrio2TDMGsnz8Q0AuhtZjBrqrHm3sNdXKJHj-ThNAmCdSeZN2dYtIuk9YbnqKdqxq6TQvH5F1yVQ23EKIK-Si27ovMKZd_TRqXYOcg-XtMhxr4VL2QUI55RZcjzs7bhl8NPFneQHffJhn7PPUn36UKEhMIJGHh4YRpVGeT8cRDZSMEbCsoXSQUvH1kOyTjJgnrC9eKYMU018jtMELoU4diIwVkJHKYidbvT134CAPBZM0trcy8KCkOjhJYbl9PQft2ELyoCHJ-YHnKnm_YPfSycArIdWh4q4FVz4IC_EZM-cdGvk4TH92f4iBOUINOioeEP9MS7TjyRT9p6KH0Jotojc2V0N7fmlcthcBqe3F9ll85q-tC4V1R0Ek3-K1quSfodSmbe8bAXdLRMYrGqa1RXh0G0H_aAbXeh7La7wZL1xOUnnAA03e9-8Q2jo_oE0ixGjMFUHqqfBN8qqNeWpOHzUZQJRtP1vb8r9g0F4S6j4MXL5rBnGsPcXQ",
                    D="217035401",
                    E="q",
                    F="login_create",
                    G="6LcxuOsUAAAAAI2IYDfxOvAZrwRg2T1E7sJq96eg",
                    H="0Z0HWX9hanGDpYuQm6nPsbrB0_Xb4OrJL-njLPMhV1E4SmxSW2JwlniBiJq8oquywObI0djrDPL4AxE3GSIpO11DSFNhh2lyeYutk5ijsde5wsmOsZdVbAYUBZBFu5JHZZftrBJP4dAWHI3oJijiGOpUdqiKdFrcXqDikP347jBSQCMIdrl_USexjxVLOa-I1znnWgclLsj4CiwSGyIwVjhBSFp8YmtygKaIkZiqzLK7wtD22OHo-x0DCBMhRykyOP4hKxEO0QMo5yGjTaPhBsknfQe0-xWX3dwpI3k8KhfN3757-cfSVFXf_e9xo73b1fSN0JW4wpj_MPacxsQCMFZsamUeYSZJUyz3LW8R45DLIV_eB5k-yPsdOyEz5SvtEBn_pTNhf5mXnk-SV3qD2eg6IN8MflyGXKpcpnyGyAo4XmSGdSZpLlFa_Je0eqjG4NLZltmewcsiLuETLU9ZU_1ABSgxi5nL0oy9uA40Dhi-VC40cbvqDBY0JtQa3AMIT3kvNRM4bpEalTKVSwVLafNk2uCy4QcRFzHPEdb6AAYbln_2hzlrhaOhnFWYXYCKPDZ_qdv2EBYsxgjN8PtExhBCXHp0iyxzNFthR4R6qMbg3uWW2Z7By7Hu4RM1UzlL_UAFKDHQApymWBGsHiRi3M5ovtCKwSJH0gAeKEJQUlRiWFp1HmEmSVNg50T3mUPFQ1Dq4Td56-4f6bdB_6GLZh-x9IJbxpdJe527obBlqLrcwsvSl7rAptEyXIMIRxlTITLs-rjLTZtcl4EXrLfYirjW8QLppumu0dvBZvEjRWNJWA1QFTvF_Bonpme2CKI0ZsD-hIp5BskmRE3oGjRSTFp0doSGjIM0ezxjabc0grDW3P7tnuHwFfgBC8zz-ZwFSC2cNniBQ3GrrZvBx7HL2eiFyI2wutTmaM48v1CDSM9ZcmFXgX6AoqSW3O8Rxx3ezeNmC0FbAigKK-msTT_1xxFDaXNxc32fka-6V5pfgohmX-7r8v0aDOJsLvC3UJ7E5qhzWNq8v0xSgJ7EutC-zOLU8u2e4abJ02I26Rs1V1VcBUgNMDnUBVOBn7m3wm-ywObI0didwMps9zhyhKrBFqSyzHbxmtVrsX9hMyCzAYbNI8XHiT9pf3lj6YOxNEoT6aPWS23AakwNl56kGgPWVMb4OixmtGqQ_v0GIJp8nlS6oMdI3nWLVKNUn7UesQPcz0lcBWNt833rhSsVy4pUTaxCfEpnfk_WCHqMikg-2BJEaekKAL5AUqQSaSI0xzDWvFKoV10C1SuRH7jzRLOlWsn7MSQBh8ID6X-OL8obmj9Np6Ir3XP6E-6QieQWgDIcPdAfAOcAanwieQpktsC2_Ms8zlSCwNNRT5SfCSudN6nz4WPFa91H6aulZAXLzkRpyFVcMnABkGpMebQ2JAnUwkPp3EHsamTmqO78dqTG3FMo0llu_Vrk1ol3AWsdS8TXaWv0103--ReF5BG3xVe50-VTnkQtcEakJagWNC28mpfKtD8IZkTKRI4FQrDHBSZUlql3RIK9o30TtbfBSwE7TS-5r4nLZiN9k_ZDtZxZp-lj5dAuXApL4nxiI_6wVkSqxOJkNoi1-Q54iow2jRqNZ1DnKSrY72mjBOr5N0l2vR9FKuHzhPfd65EXuSuyMCZPwURSX-3Ilox-HLWsptvWUDogUkDl8MrNEqDqOVM0pylHeHMJZnR_VYeAmvCq1TMha2nn7U_Z49oEFR9lyBofleB5vIGD3fRqFGIPliQCpKbQolBCdMJgzoyTOIswwoTrUOtpMwk28NLtd8GfJQvJi0zHybNdt3HPYWPp80HEBVfKPDJgkoACh_6QjrDSQDpMPfRKcGrgFkzueQY07tky0MbderFnlaOBn5UPyQ_Fsz1m0Vc1i5WHqauOC3HLdQMxT2V3Zh9iJ0pQBiwmIH48YliiH6nb_hgCEMYIzfD7CWdUvt0DNOc9Byzu9O_JowW3Hd9JN1kPPd8Nj5GwGf99l75jalACiCJX8dQeNIojyoRCFG5cxm_t9HMIsvkGlIqUoyje5Q7ZA6SukSsc8r0myaO5XzXH-YOOK1XkGT95p5nvtae9vI4cqY-eY-bEHojdk8Hf-fASr_K32uCHPMZcw0BeaINFk4xKeKq4urDGxNbRhsmOsbtJi0zbCSdBQzn3Of8iKD18HYxaEEK8foiGfBKo5vUC1HcQevz7CNLMQ1SWrUpsMmB-nKqhTpFWeYMlr2X3ZXvhH9mfZiQ6UB47xd-po9W_-b_id-oXrf_2oDocGpy6rFb4ctA26JK8QgAyVFZ4cxxjJEtQ_qF_FXuts7z24dP1Bvln5bN16A0wMadKGBZraffNlAaMOjh-JN4Evs_t_DYMmkhO5LZFDqRCmS7MZumPNReM912OvO7U28EnaTtJP9FTSdumNCnL_lOV2_VnzlP1h_oIWeyCRHaHzjh6dDWz4fweEDbMEtf7ALqZemyurDpojqCutVaYxrjKuX6hq03_yZMVqCoD5YwZpGX3_ksxY32XpZRNkFV4BjxqONaoRlj2yTLgGvTHISoIOlR2aHKEfqCelK9Um1yDibthTAFQFRftpCnnJZ-BTzW8OaBF89obidCKpDIgptxWJLopCkRCbQ8AnyfqGDZMZmkGSQ4xO50HMaqdr0kvLac5IAFPDZuBW11_ahRFpGJr3Vuxq_nn6hiRk2GTrcfR5H3AhaiyOOpFLrhikTI8ulDa-Pc473Wi9WMUn3GzHVdlK008AY_Z403Hag-5c4UsWatFe81cNoBd9B4UEpBKV86f7ihi-M7k3mSy1MrNWtjejEck5r1THUb9JuS3yUM4002PPVdBXwH7LV8Ne0EkYatZtFXnfcQBlKH8ejiuND2Ludfx6A6n6q_S2F7wtsy_aMJEWzDi0PcNrxmjsP_NKyzLtKLQ7wkDDb_E"
                )
            
            serialized_data = proto_data.SerializeToString()

            headers = {'Content-Type': 'application/x-protobuffer'}
            upload_url = "https://www.google.com/recaptcha/api2/reload?k=6LcxuOsUAAAAAI2IYDfxOvAZrwRg2T1E7sJq96eg"
            upload_response = requests.post(upload_url, data=serialized_data, headers=headers)
            
            # Process the response
            result = upload_response.text.split(',')[1].replace("\"", "")
            return result

        except Exception as e:
            return f"Error: {str(e)}"
