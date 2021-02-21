import pytest

def test_list():
    """
    在python中变量是引用式变量，一般讲到变量和对象的关系的时候
    我们可以这么理解，变量就是对象的便利贴，一个对象可以有好多
    变量来对应，一般我们不会说把对象分配给变量，而是讲将变量分
    配给对象
    """
    a = [1,2,3]
    b = a #这里不是拷贝，而是加了引用别名
    a.append(4)
    assert 4 == len(a)
    assert 4 == a[-1]
    assert id(a) == id(b)
    # 下面通过构造函数或者[:]的操作进行了浅拷贝，只拷贝了list最外层容器
    # 的内容，因此和原来的a就不一样了
    c = list(a)
    assert id(c) != id(a)
    d = a[:]
    assert id(d) != id(a)

class Gizmo:
    def __init__(self):
        print("Gizmo id is {0}".format(id(self)))

def test_gizmo():
    """
    理解python的赋值语句，应该始终先读右边的代码，对象在右边创建
    或者获取，然后左边的变量才会绑定到对象上。
    """
    x = Gizmo()
    with pytest.raises(TypeError):
        y = Gizmo() * 10

def test_name():
    charles = {'name' : "Charles", 'born' : 1932}
    lewis = charles
    assert lewis is charles
    assert id(lewis) == id(charles)

    alex = {'name' : "Charles", 'born' : 1932}
    # alex和charles这两个变量对应的对象不是同一个对象
    # 但是==是通过dict中的eq方法进行比较的，因此==只对比内存地址中内容
    # 是否相同，而is比较的其实是两个对象的内存地址是否相同，id函数的作
    # 用就是获取内存地址的位置，id一定是唯一的数值标注，而且在对象的生
    # 命周期内是不变的
    assert charles == alex
    assert alex is not charles
    assert id(alex) != id(charles)

def test_tuple_mutable():
    t1 = (1, 2, [30, 40])
    t2 = (1, 2, [30, 40])
    assert t1 == t2
    assert t1 is not t2
    assert id(t1) != id(t2)
    pre_id = id(t1[-1])
    t1[-1].append(50)
    assert pre_id == id(t1[-1])
    assert t1 != t2

def test_shadow_copy():
    l1 = [3, [55, 44], (7,8,9)]
    # 这个里的list构造函数只是做了一个浅拷贝，l2里面的元素只是一些新的
    # 变量引用，而实际的对象却没有变过，即[55,44]和(7,8,9)对象没有被实
    # 际拷贝
    l2 = list(l1)
    # 一般构造方法和[:]做的都是浅拷贝
    assert l1 == l2
    assert id(l1) != id(l2)
    assert l1 is not l2
    assert id(l1[1]) == id(l2[1])
    assert l1[1] is l2[1]
    assert id(l1[2]) == id(l2[2])
    assert l1[2] is l2[2]

    l1.append(100)
    assert l1 != l2

    l1[1] += [33,22]
    # 对于可变对象来说，l1[1]引用的是列表，+=运算符就是就地修改列表，
    # 但是对于元祖来说，+=则是会新建一个新的内存地址存放新元祖
    assert id(l1[1]) == id(l2[1])
    l2[2] += (10,11)
    assert id(l1[2]) != id(l2[2])

class Bus:
    def __init__(self, passengers = None):
        if passengers is None:
            self.passengers = []
        else:
            self.passengers = passengers

        def pick(self, name):
            self.passengers.append(name)

        def drop(self, name):
            self.passengers.remove(name)

def test_deep_copy():
    import copy
    bus1 = Bus(['Alice', 'Bill', 'Claire', 'David'])
    bus2 = copy.copy(bus1)
    bus3 = copy.deepcopy(bus1)
    assert id(bus1.passengers) == id(bus2.passengers)
    assert id(bus1.passengers) != id(bus3.passengers)

def test_pass_by_ref():
    def f(a,b):
        a += b
        return a
    a = [1,2]
    b = [3,4]
    c = f(a,b)
    assert c == a
    assert id(c) == id(a)
    # 如果传入的是一个列表就很危险，因为他会把原来的传入列表给改了
    a = (1,2)
    b = (3,4)
    c = f(a,b)
    assert a != c
    assert id(a) != id(c)
    # 如果传入的是一个元组，元组遇到+=不会就地操作，会新开辟一块地方

def test_dont_use_mutalbe_type_as_default_value():
    class HauntedBus:
        def __init__(self, passengers = []):
            self.passengers = passengers
        def pick(self, name):
            self.passengers.append(name)
        def drop(self, name):
            self.passengers.remove(name)
    # 没有制定初始化乘客的HauntedBus实例会共享同一个乘客列表
    bus1 = HauntedBus()
    bus1.pick('alice')
    bus2 = HauntedBus()
    assert bus1.passengers == bus2.passengers
    assert id(bus1.passengers) == id(bus2.passengers)

    assert id(HauntedBus.__init__.__defaults__[0]) == id(bus1.passengers)

def test_del():
    import weakref
    s1 = {1,2,3}
    s2 = s1;
    def bye():
        print('Gone with the wind...')
    #这里弱引用绑定的函数bye千万不能是s1所指对象的绑定方法，这样就无法做对象
    #析构了
    ender = weakref.finalize(s2, bye)
    assert ender.alive
    del s1
    assert ender.alive
    s2 = 'hello world'
    assert ender.alive == False

def test_weak_ref():
    import weakref
    a_set = {0,1}
    wref = weakref.ref(a_set)
    assert a_set == wref()
    assert id(a_set) == id(wref())
    a_set = {2,3,4}
    assert wref() is None

    class Cheese:
        def __init__(self, kind):
            self.kind = kind

    stock = weakref.WeakValueDictionary()
    catalog = [Cheese('Red'), Cheese('Tilist'), Cheese('Brie')]
    for cheese in catalog:
        stock[cheese.kind] = cheese
    sorted(stock.keys())
    del catalog
    assert len(list(stock.keys())) == 1
    del cheese
    assert len(list(stock.keys())) == 0





