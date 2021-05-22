
class AutoSerialNumber(object):
    """创建OA单号"""

    def __init__(self):
        # J201906120001
        # self.fd_apply_no = ApplicationBasicFormModel.delete_objects.filter(fd_apply_no__contains="J").order_by(
        #     "-fd_apply_no").first().fd_apply_no
        self.fd_apply_no = "J20196120001"
        self.date_str = self.fd_apply_no[1: 9]  # 日期字符串
        self._serial_number = self.fd_apply_no[9:]  # 流水号字符串
        self._serial_number = 0  # 流水号

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        if isinstance(value, int):
            self._serial_number = value
        else:
            self._serial_number = 1

    def __iter__(self):
        return self

    def __next__(self):
        self.serial_number += 1
        # 生成一个固定4位数的流水号
        return "{0:03d}".format(self.serial_number)

    def __call__(self, *args, **kwargs):
        # 返回生成序列号(日期加流水号)
        return "J" + self.date_str + next(self)

    # 时间格式化,最好是用定时器来调用该方法
    def timed_clear_serial_number(self):
        """用于每天定时清除流水号"""

        self.serial_number = 1
        self.date_str = time.strftime("%Y%m%d", time.localtime(time.time()))

'''
使用方法:

1.在类视图中创建一个类属性,在请求方法中,需要的时候使用self.类属性的方法调用,

2.需要开启一个定时器,每天将serial_number和date_str重置更新一下,在定时器中更新时,需要使用类视图.类属性,否则第二天你会发你更新根本不是那个类属性的数值

在项目当中使用需要将你的需要生成流程单号的那个模型在流程单号类的初始化方法中进行一次最后一条数据的查询,拿出单号,进行分解

优点:仅仅在项目重启的时候进行一次数据库查询,无并发问题,不会出现什么单号重复导致数据存不进去,因为所有的请求对象使用的是一个流程单号生成对象
'''