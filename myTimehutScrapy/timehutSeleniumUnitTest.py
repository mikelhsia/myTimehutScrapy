import timehutSeleniumToolKit as tstk

import unittest
import sys
import math
import time
import os

if os.getenv("TIMEHUT_DEBUG") is not None:
    import pdb
    pdb.set_trace()


def progressBar(cur, total):
    percent = '{:.2%}'.format(cur / total)
    sys.stdout.write('\r')
    sys.stdout.write("[%-50s] %s" % ('=' * int(math.floor(cur * 50 / total)), percent))
    sys.stdout.flush()


class MyTest(unittest.TestCase):  # 继承unittest.TestCase
    @classmethod
    def tearDownClass(cls):
        # 必须使用@classmethod 装饰器, 所有test运行完后运行一次
        print('End Timehut testing')
        print('----------------------------------')

    @classmethod
    def setUpClass(cls):
        # 必须使用@classmethod 装饰器,所有test运行前运行一次
        print('----------------------------------')
        print('Start Timehut testing')

    def tearDown(self):
        # 每个测试用例执行之后做操作
        # print('Tearing down the test env ...')
        # os.system('rm -rf ./*.png')
        self.timehut.quitTimehutPage()
        # print('Done tearing down the test env')

    def setUp(self):
        # 每个测试用例执行之前做操作
        # print('Setting up for the test ...')
        self.isHeadless = False
        self.timehut = tstk.timehutSeleniumToolKit(self.isHeadless)
        timehutUrl = "https://www.shiguangxiaowu.cn/zh-CN"

        self.timehut.fetchTimehutContentPage(timehutUrl)

        if not self.timehut.loginTimehut('mikelhsia@hotmail.com', 'f19811128'):
            print(' [*] Login failed')
            return False

        print(' [x] Login success')
        # print('Done setting up for the test')

    def test_a_run(self):
        print('\n### Testing behavior of scrolling down to trigger ajax call to get more content')
        test_result = 0
        test_target = 3

        # Testing Scrolling down to trigger another ajax
        for i in range(0, test_target):
            self.timehut.scrollDownTimehutPage2()
            if self.timehut.whereami(i):
                test_result += 1
            progressBar(test_result, test_target)

        self.assertEqual(test_target, test_result)  # 测试用例

    def test_b_run(self):
        print('\n### Testing behavior of switching baby id')
        ONON_ID = 537413380
        MUIMUI_ID = 537776076

        mui_mui_homepage = self.timehut.getTimehutPageUrl().replace(ONON_ID.__str__(), MUIMUI_ID.__str__())
        self.timehut.fetchTimehutContentPage(mui_mui_homepage)
        self.assertEqual(True, self.timehut.whereami('mui_mui'))  # 测试用例

    def test_c_run(self):
        print('\n### Testing behavior of fetching album list')
        num = self.timehut.getTimehutAlbumURLSet()

        self.assertNotEqual(0, num)  # 测试用例

    def test_d_run(self):
        print("### Testing behavior of fetching album catalog")
        timehutCatalog = self.timehut.getTimehutCatalog()

        for k in timehutCatalog:
            print(f'{k}: {timehutCatalog[k]}')

        start = input(f'Select a date you would like to start with: \n')
        self.timehut.selectTimehutCatalog(int(start))
        self.timehut.scrollDownTimehutPage2()

        print(self.timehut.getTimehutRecordedCollectionRequest())
        self.assertEqual(True, isinstance(timehutCatalog, dict))  # 测试用例


if __name__ == '__main__':
    # unittest.main()  # 运行所有的测试用例

    # unittest.main() # 使用main()直接运行时，将按case的名称顺序执行
    suite = unittest.TestSuite()

    # 将需要执行的case添加到Test Suite中，没有添加的不会被执行
    # suite.addTest(MyTest('test_a_run'))
    # suite.addTest(MyTest('test_b_run'))
    # suite.addTest(MyTest('test_c_run'))
    suite.addTest(MyTest('test_d_run'))
    unittest.TextTestRunner().run(suite)  # 将根据case添加的先MyTest后顺序执行
