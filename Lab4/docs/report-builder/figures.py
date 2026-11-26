"""PDF versions of the four Mermaid diagrams in REPORT.md (same classes, same relations)."""

from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib import colors

from styles import ABSTRACT_FILL, IFACE_FILL, NAVY, USABLE
from uml import Box, connect, fan_in, fit, note, sequence, tree

CLIENT_FILL = colors.HexColor("#EDEDF3")
ROLE_FILL = colors.HexColor("#E6F0FA")
CONCRETE_FILL = colors.HexColor("#EAF4EC")
CREATE_FILL = colors.HexColor("#FFF8E6")


def fig_strategy():
    d = Drawing(USABLE, 480)
    shell = Box(150, 470, 170, "TradeShell", stereo="Client", fill=CLIENT_FILL,
                methods=["- Method(args)   (typed: method hifo)"])
    account = Box(0, 395, 215, "TradingAccount", stereo="Context", fill=ROLE_FILL,
                  attrs=["- _lotSelection: ILotSelectionStrategy"],
                  methods=["+ LotSelection: ILotSelectionStrategy",
                           "+ UseLotSelection(lotSelection)",
                           "+ Sell(symbol, quantity, price, date): TradeReceipt"])
    factory = Box(255, 395, 215, "LotSelectionFactory", stereo="Factory Method", fill=CREATE_FILL,
                  methods=["+ Register(name, creator)", "+ Create(name): ILotSelectionStrategy"])
    strategy = Box(110, 285, 235, "ILotSelectionStrategy", stereo="Strategy interface",
                   abstract=True, fill=IFACE_FILL,
                   attrs=["+ Name: string"],
                   methods=["+ Select(lots, quantity): IReadOnlyList<LotPick>*"])
    pick = Box(385, 285, 85, "LotPick", attrs=["+ Lot: Lot", "+ Quantity: decimal"])
    concretes = [Box(x, 180, 145, name, stereo="ConcreteStrategy", fill=CONCRETE_FILL,
                     attrs=["+ Name = %s" % short],
                     methods=["+ Select(lots, quantity)", "   %s" % rule])
                 for x, name, short, rule in [
                     (0, "FifoSelection", "\"FIFO\"", "oldest lot first"),
                     (162, "LifoSelection", "\"LIFO\"", "newest lot first"),
                     (325, "HighestCostSelection", "\"HIFO\"", "highest unit cost first")]]
    helper = Box(135, 80, 200, "LotPicking", stereo="static helper",
                 methods=["+ TakeInOrder(orderedLots, quantity)  {static}"])
    for b in [shell, account, factory, strategy, pick, helper] + concretes:
        b.draw(d)
    connect(d, [(180, shell.bottom), (180, account.y)], "assoc",
            label="UseLotSelection(...)", label_at=(132, (shell.bottom + account.y) / 2 - 2))
    connect(d, [(290, shell.bottom), (290, factory.y)], "assoc",
            label="Create(name)", label_at=(324, (shell.bottom + factory.y) / 2 - 2))
    connect(d, [(150, account.bottom), (150, strategy.y)], "aggregate",
            label="current method  1", label_at=(196, (account.bottom + strategy.y) / 2 - 2))
    connect(d, [(330, factory.bottom), (330, strategy.y)], "dep",
            label="creates", label_at=(352, (factory.bottom + strategy.y) / 2 + 6))
    connect(d, [(strategy.right, 262), (pick.x, 262)], "dep", label="returns", label_at=(365, 266))
    tree(d, strategy, concretes, 200, kind="realize")
    fan_in(d, concretes, helper, 100, kind="dep")
    return fit(d)


def fig_command():
    d = Drawing(USABLE, 480)
    shell = Box(0, 470, 150, "TradeShell", stereo="Client", fill=CLIENT_FILL,
                methods=["- buy / sell / undo / redo"])
    history = Box(230, 470, 240, "TradeHistory", stereo="Invoker", fill=ROLE_FILL,
                  attrs=["- _done: Stack<ITradeCommand>", "- _undone: Stack<ITradeCommand>"],
                  methods=["+ Execute(command)", "+ Undo(): ITradeCommand", "+ Redo(): ITradeCommand",
                           "+ Done: IReadOnlyList<ITradeCommand>"])
    iface = Box(230, 345, 240, "ITradeCommand", stereo="Command interface", abstract=True,
                fill=IFACE_FILL, attrs=["+ Description: string"],
                methods=["+ Execute()*", "+ Undo()*"])
    base = Box(230, 245, 240, "TradeCommand", stereo="abstract", abstract=True, fill=ABSTRACT_FILL,
               attrs=["# Account: TradingAccount", "+ Receipt: TradeReceipt"],
               methods=["# Place(): TradeReceipt*", "+ Execute()   first run: Place(); redo: Reapply",
                        "+ Undo()   Account.Reverse(Receipt)"])
    buy = Box(230, 125, 115, "BuyCommand", stereo="ConcreteCommand", fill=CONCRETE_FILL,
              methods=["# Place(): Account.Buy(...)"])
    sell = Box(355, 125, 115, "SellCommand", stereo="ConcreteCommand", fill=CONCRETE_FILL,
               methods=["# Place(): Account.Sell(...)"])
    account = Box(25, 345, 165, "TradingAccount", stereo="Receiver", fill=ROLE_FILL,
                  methods=["+ Buy(...): TradeReceipt", "+ Sell(...): TradeReceipt",
                           "+ Reverse(receipt)", "+ Reapply(receipt)"])
    receipt = Box(25, 150, 165, "TradeReceipt",
                  attrs=["+ Trade: Trade", "+ Added: IReadOnlyList<Lot>", "+ Removed: IReadOnlyList<Lot>"])
    for b in (shell, history, iface, base, buy, sell, account, receipt):
        b.draw(d)
    connect(d, [(shell.right, 448), (history.x, 448)], "assoc",
            label="Execute / Undo / Redo", label_at=(190, 452))
    connect(d, [(350, history.bottom), (350, iface.y)], "aggregate",
            label="done / undone  0..*", label_at=(400, (history.bottom + iface.y) / 2 - 2))
    connect(d, [(350, base.y), (350, iface.bottom)], "realize")
    tree(d, base, [buy, sell], 140, kind="inherit")
    connect(d, [(base.x, 236), (account.cx, 236), (account.cx, account.bottom)], "assoc",
            label="receiver", label_at=(170, 240))
    connect(d, [(base.x, 168), (210, 168), (210, 123), (receipt.right, 123)], "assoc",
            label="keeps", label_at=(212, 172))
    connect(d, [(60, account.bottom), (60, receipt.y)], "dep",
            label="returns", label_at=(80, 210))
    # The client creates the concrete commands: routed round the left and under the boxes.
    connect(d, [(8, shell.bottom), (8, 60), (buy.cx, 60), (buy.cx, buy.bottom)], "dep",
            label="creates", label_at=(110, 64))
    connect(d, [(buy.cx, 60), (sell.cx, 60), (sell.cx, sell.bottom)], "dep")
    return fit(d)


def fig_observer():
    d = Drawing(USABLE, 480)
    shell = Box(0, 470, 150, "TradeShell", stereo="Client", fill=CLIENT_FILL,
                methods=["- Watch(args, subscribe)"])
    subject = Box(230, 470, 240, "ITradeSubject", stereo="Subject interface", abstract=True,
                  fill=IFACE_FILL, methods=["+ Subscribe(observer)*", "+ Unsubscribe(observer)*"])
    account = Box(230, 385, 240, "TradingAccount", stereo="ConcreteSubject", fill=ROLE_FILL,
                  attrs=["- _observers: List<ITradeObserver>", "- _notifying: bool"],
                  methods=["+ Subscribe(observer)", "+ Unsubscribe(observer)",
                           "- Notify(kind, trade)   loops over a copy"])
    event = Box(0, 385, 170, "TradeEvent",
                attrs=["+ Kind: Executed | Reversed", "+ Trade: Trade", "+ Lots: IReadOnlyList<Lot>"])
    observer = Box(150, 262, 200, "ITradeObserver", stereo="Observer interface", abstract=True,
                   fill=IFACE_FILL, methods=["+ OnTrade(change: TradeEvent)*"])
    concretes = [
        Box(0, 175, 150, "ActivityLog", stereo="ConcreteObserver", fill=CONCRETE_FILL,
            attrs=["+ Entries: IReadOnlyList<string>"], methods=["+ OnTrade(change)"],
            tag="[log] one line per trade or undo"),
        Box(160, 175, 150, "RealisedGainsTracker", stereo="ConcreteObserver", fill=CONCRETE_FILL,
            attrs=["+ Total: decimal"], methods=["+ OnTrade(change)"],
            tag="[gains] the taxed running total"),
        Box(320, 175, 150, "ConcentrationAlert", stereo="ConcreteObserver", fill=CONCRETE_FILL,
            attrs=["- _limitPercent: decimal", "+ Alerts: IReadOnlyList<string>"],
            methods=["+ OnTrade(change)"], tag="[alert] one holding above the limit"),
    ]
    for b in [shell, subject, account, event, observer] + concretes:
        b.draw(d)
    connect(d, [(shell.right, 448), (subject.x, 448)], "assoc",
            label="watch / unwatch", label_at=(190, 452))
    connect(d, [(350, account.y), (350, subject.bottom)], "realize")
    connect(d, [(300, account.bottom), (300, observer.y)], "aggregate",
            label="notifies  0..*", label_at=(338, (account.bottom + observer.y) / 2 - 2))
    connect(d, [(observer.x, observer.cy), (85, observer.cy), (85, event.bottom)], "dep",
            label="receives", label_at=(112, observer.cy + 4))
    tree(d, observer, concretes, 195, kind="realize")
    return fit(d)


def fig_interaction():
    d = Drawing(540, 330)
    labels = ["User", "TradeShell", "TradeHistory", "SellCommand", "TradingAccount",
              "HighestCostSelection", "PortfolioAccessProxy", "ITradeObserver"]
    messages = [
        (0, 1, "1: sell ETH 2", "call"),
        (1, 2, "2: Execute(sellCommand)", "call"),
        (2, 3, "3: Execute()", "call"),
        (3, 4, "4: Sell(ETH, 2, ...)", "call"),
        (4, 6, "5: Lots - View allowed", "call"),
        (4, 5, "6: Select(ethLots, 2)", "call"),
        (5, 4, "7: 1.5 @ 3,900 + 0.5 @ 2,300", "ret"),
        (4, 6, "8: RemoveLot / AddLot - Trade allowed", "call"),
        (4, 7, "9: OnTrade(TradeEvent)", "call"),
        (4, 3, "10: TradeReceipt", "ret"),
        (3, 2, "11: done", "ret"),
        (2, 2, "12: push on the undo stack", "call"),
    ]
    sequence(d, labels, messages, top=330, step=25, width=540,
             frames=[("loop [each subscribed observer]", 8, 8, 4, 7)])
    return fit(d)


FIGURES = {
    "strategy": fig_strategy,
    "command": fig_command,
    "observer": fig_observer,
    "interaction": fig_interaction,
}
