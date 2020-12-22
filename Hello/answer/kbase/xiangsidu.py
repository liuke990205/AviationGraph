def editDistDP(s1, s2):
    m = len(s1)
    n = len(s2)
    # 创建一张表格记录所有子问题的答案
    dp = [[0 for x in range(n + 1)] for x in range(m + 1)]

    # 从上往下填充DP表格
    for i in range(m + 1):
        for j in range(n + 1):

            # 如果第一个字符串为空，唯一的编辑方法就是添加第二个字符串
            if i == 0:
                dp[i][j] = j  # Min. operations = j

            # 如果第二个字符串为空，唯一的方法就是删除第一个字符串中的所有字母
            elif j == 0:
                dp[i][j] = i  # Min. operations = i

            # 如果两个字符串结尾字母相同，我们就可以忽略最后的字母
            elif s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]

                # 如果结尾字母不同，那我们就需要考虑三种情况，取最小的编辑距离
            else:
                dp[i][j] = 1 + min(dp[i][j - 1],  # 添加
                                   dp[i - 1][j],  # 删除
                                   dp[i - 1][j - 1])  # 替换

    return dp[m][n]
