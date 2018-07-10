import unittest


def func(strlist: list, k):  # 列表长度k

    if strlist == []:
        return ''
    elif len(strlist) < k:
        return ''

    finally_list = []
    for i in range(len(strlist)):
        j = i  # 循环变量j
        finally_str = ''
        try:
            while j < k + i:
                finally_str = finally_str + strlist[j]
                j = j + 1
            finally_list.append(finally_str)
        except:
            pass

    for i in range(len(finally_list)):
        for j in range(len(finally_list) - 1):
            if len(finally_list[j]) < len(finally_list[j + 1]):
                finally_list[j], finally_list[j + 1] = finally_list[j + 1], finally_list[j]
            else:
                pass

    print(finally_list)


func(['this', 'is', 'an', 'example', 'e', 'kkk', 'kangguixi', 'houzi'], 1)
func(['this', 'is', 'another', 'example'], 2)
func(['this', 'is', 'another', 'example', 'e', 'kkk', 'kangguixi', 'houzi'], 4)


# class DefaultTestCase(unittest.TestCase):
#
#     def test_func(self):
#         self.assertEqual(func(['this', 'is', 'an', 'example'], 1), 'example')
#         self.assertEqual(func(['this', 'is', 'another', 'example'], 1), 'another')
#         self.assertEqual(func(['this', 'is', 'another', 'example'], 2), 'anotherexample')
#
#         self.assertEqual(func([], 1), '')
#         self.assertEqual(func(['this', 'is', 'an', 'example'], 5), '')
#         self.assertEqual(func(['this', 'is', 'an', 'example'], 0), '')
#         print('ok')
#
#
# default_test_case = DefaultTestCase()
# default_test_case.test_func()
