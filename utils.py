def sorted_room(rooms):
    room_m = []
    room_nm = []
    for room in rooms:
        if len(room.messages) > 0:
            room_m.append(room)
        else:
            room_nm.append(room)
    rooms = []
    if room_m:
        rooms = sorted(room_m, key=lambda messages: messages.messages[0].date, reverse=True)
    for r in room_nm:
        rooms.append(r)
    return rooms
