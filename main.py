import os, asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from pocketoptionapi import PocketOptionAPI

BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
PO_SSID=os.getenv("POCKET_OPTION_SSID")
api=PocketOptionAPI(PO_SSID,is_demo=True)
ACTIVE=False; PROFIT=0.0; STAKE=1.0; PAIR="EURUSD_otc"; EXPIRY=5

async def menu(update,context):
 global ACTIVE; ACTIVE=False
 try: await api.connect(); bal=await api.get_balance()
 except: bal="?"
 txt=f"OTC 5s BOT\n{PAIR} {EXPIRY}s {STAKE}$\nBal {bal}$ PnL {PROFIT}$\nAuto -20.75$ / +{STAKE*10}$"
 kb=[ [InlineKeyboardButton("EURUSD_otc",callback_data="pair_EURUSD_otc"),InlineKeyboardButton("AUDCAD_otc",callback_data="pair_AUDCAD_otc")], [InlineKeyboardButton("5s",callback_data="exp_5"),InlineKeyboardButton("15s",callback_data="exp_15"),InlineKeyboardButton("30s",callback_data="exp_30"),InlineKeyboardButton("1m",callback_data="exp_60")], [InlineKeyboardButton("1$",callback_data="stake_1"),InlineKeyboardButton("1.5$",callback_data="stake_1.5"),InlineKeyboardButton("2$",callback_data="stake_2")], [InlineKeyboardButton(f"TRADE {PAIR}",callback_data="trade"),InlineKeyboardButton("🛑 STOP",callback_data="stop")] ]
 if update.message: await update.message.reply_text(txt,reply_markup=InlineKeyboardMarkup(kb))
 else: await update.callback_query.edit_message_text(txt,reply_markup=InlineKeyboardMarkup(kb))

async def handle(update: Update,context: ContextTypes.DEFAULT_TYPE):
 global PAIR,EXPIRY,STAKE,ACTIVE,PROFIT
 q=update.callback_query; await q.answer(); d=q.data
 if d.startswith("pair_"): PAIR=d.replace("pair_",""); await menu(q,context); return
 if d.startswith("exp_"): EXPIRY=int(d.replace("exp_","")); await menu(q,context); return
 if d.startswith("stake_"): STAKE=float(d.replace("stake_","")); await menu(q,context); return
 if d=="stop": ACTIVE=False; await q.edit_message_text(f"🛑 STOPPED\nPnL {PROFIT}$\n/start"); return
 if d=="trade":
  ACTIVE=True; stake=STAKE; step=0
  max_loss=-20.75 if STAKE==1 else -STAKE*20.75; max_profit=STAKE*10
  while ACTIVE and step<4:
   try:
    candles=await api.get_candles(PAIR,60,30); closes=[c[2] for c in candles]; ema9=sum(closes[-9:])/9; ema21=sum(closes[-21:])/21
    direction="call" if ema9>ema21 else "put"
    await q.edit_message_text(f"{PAIR} {direction.upper()} {stake:.2f}$ {EXPIRY}s Step {step+1}/4 PnL {PROFIT:.2f}$",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛑 STOP",callback_data="stop")]]))
    oid=await api.buy(PAIR,stake,direction,EXPIRY); await asyncio.sleep(EXPIRY+2); win=await api.check_win(oid); PROFIT+=win
    if win>0: break
    stake*=2.3; step+=1
    if PROFIT<=max_loss or PROFIT>=max_profit: ACTIVE=False; break
   except Exception as e: await q.edit_message_text(f"Error {e}\n/start"); ACTIVE=False; break
  await q.edit_message_text(f"Done PnL {PROFIT:.2f}$",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("TRADE AGAIN",callback_data="trade"),InlineKeyboardButton("Menu",callback_data="menu")]]))
 if d=="menu": await menu(q,context)

def main():
 app=Application.builder().token(BOT_TOKEN).build()
 app.add_handler(CommandHandler("start",menu))
 app.add_handler(CallbackQueryHandler(handle))
 app.run_polling()
if __name__=="__main__": main()