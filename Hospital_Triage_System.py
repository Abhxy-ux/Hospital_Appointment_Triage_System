import heapq

class Patient:
    def __init__(self, pid, name, age, severity):
        self.id = pid
        self.name = name
        self.age = age
        self.severity = severity

class SlotNode:
    def __init__(self, slotId, startTime, endTime):
        self.slotId = slotId
        self.startTime = startTime
        self.endTime = endTime
        self.status = "FREE"
        self.next = None

class Doctor:
    def __init__(self, did, name, specialization):
        self.id = did
        self.name = name
        self.specialization = specialization
        self.scheduleHead = None

class CircularQueue:
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = -1
        self.rear = -1
        self.size = 0

    def enqueue(self, token):
        if self.size == self.capacity:
            return "FULL"
        if self.front == -1:
            self.front = 0
        self.rear = (self.rear + 1) % self.capacity
        self.queue[self.rear] = token
        self.size += 1
        return "OK"

    def dequeue(self):
        if self.size == 0:
            return None
        token = self.queue[self.front]
        if self.front == self.rear:
            self.front = -1
            self.rear = -1
        else:
            self.front = (self.front + 1) % self.capacity
        self.size -= 1
        return token

    def peek(self):
        if self.size == 0:
            return None
        return self.queue[self.front]

class UndoStack:
    def __init__(self):
        self.stack = []

    def push(self, action):
        self.stack.append(action)

    def pop(self):
        if len(self.stack) == 0:
            return None
        return self.stack.pop()

class HospitalSystem:
    def __init__(self):
        self.doctors = {}
        self.patients = {}
        self.routineQueue = CircularQueue(50)
        self.emergencyHeap = []
        self.undoLog = UndoStack()
        self.served = []

    def addDoctor(self, did, name, specialization):
        self.doctors[did] = Doctor(did, name, specialization)

    def scheduleSlot(self, did, sid, st, et):
        node = SlotNode(sid, st, et)
        doc = self.doctors[did]
        if doc.scheduleHead is None:
            doc.scheduleHead = node
        else:
            p = doc.scheduleHead
            while p.next:
                p = p.next
            p.next = node

    def registerPatient(self, pid, name, age, severity):
        self.patients[pid] = Patient(pid, name, age, severity)

    def bookRoutine(self, token):
        r = self.routineQueue.enqueue(token)
        if r == "OK":
            self.undoLog.push(("book", token))
            return "Booked"
        return "Queue Full"

    def emergencyIn(self, pid, severity):
        heapq.heappush(self.emergencyHeap, (severity, pid))
        self.undoLog.push(("emergency", (severity, pid)))
        return "Emergency Added"

    def serveNext(self):
        if self.emergencyHeap:
            sev, pid = heapq.heappop(self.emergencyHeap)
            self.served.append(pid)
            self.undoLog.push(("serveE", pid))
            return f"Emergency Served: {pid}"
        t = self.routineQueue.dequeue()
        if t is None:
            return "No patient"
        self.served.append(t)
        self.undoLog.push(("serveR", t))
        return f"Routine Served: {t}"

    def undo(self):
        action = self.undoLog.pop()
        if action is None:
            return "Nothing to undo"
        t, val = action
        if t == "book":
            self.routineQueue.rear = (self.routineQueue.rear - 1) % self.routineQueue.capacity
            self.routineQueue.size -= 1
        elif t == "emergency":
            self.emergencyHeap.remove(val)
            heapq.heapify(self.emergencyHeap)
        elif t == "serveE":
            self.emergencyHeap.append((self.patients[val].severity, val))
            heapq.heapify(self.emergencyHeap)
            self.served.remove(val)
        elif t == "serveR":
            self.routineQueue.enqueue(val)
            self.served.remove(val)
        return "Reverted"

    def report(self):
        print("-----REPORT-----")
        print("Pending Routine:", self.routineQueue.size)
        print("Pending Emergency:", len(self.emergencyHeap))
        print("Served:", len(self.served))
        print("----------------")

system = HospitalSystem()

system.addDoctor(1, "Dr. A", "Cardiology")
system.scheduleSlot(1, 101, "10:00", "10:30")
system.scheduleSlot(1, 102, "10:30", "11:00")

while True:
    print("1 Register Patient")
    print("2 Book Routine Appointment")
    print("3 Add Emergency Case")
    print("4 Serve Next")
    print("5 Undo Last Action")
    print("6 Report")
    print("7 Exit")
    ch = int(input("Enter: "))

    if ch == 1:
        i = int(input("Patient ID: "))
        n = input("Name: ")
        a = int(input("Age: "))
        s = int(input("Severity: "))
        system.registerPatient(i, n, a, s)
        print("Registered")

    elif ch == 2:
        t = input("Token: ")
        print(system.bookRoutine(t))

    elif ch == 3:
        pid = int(input("Patient ID: "))
        sev = int(input("Severity: "))
        print(system.emergencyIn(pid, sev))

    elif ch == 4:
        print(system.serveNext())

    elif ch == 5:
        print(system.undo())

    elif ch == 6:
        system.report()

    else:
        break
