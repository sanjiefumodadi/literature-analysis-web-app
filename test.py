import csv
import matplotlib.pyplot as plt

def read_csv_and_calculate_mean(file_path):
    column_sums = {}
    column_counts = {}

    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        headers = csv_reader.fieldnames

        for header in headers:
            column_sums[header] = 0.0
            column_counts[header] = 0

        for row in csv_reader:
            for header in headers:
                try:
                    value = float(row[header])
                    column_sums[header] += value
                    column_counts[header] += 1
                except ValueError:
                    continue

    column_means = {}
    for header in headers:
        if column_counts[header] > 0:
            column_means[header] = column_sums[header] / column_counts[header]
    return column_means

def plot_bar_chart(column_means):
    if not column_means:
        print("没有可绘制的数字列")
        return

    columns = list(column_means.keys())
    means = list(column_means.values())

    plt.figure(figsize=(10, 6))
    plt.bar(columns, means, color='skyblue')
    plt.xlabel('指标')
    plt.ylabel('平均值')
    plt.title('作物数据平均值柱状图')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    csv_file = "data.csv.txt"  # 你的文件路径
    means = read_csv_and_calculate_mean(csv_file)
    print("各指标平均值：")
    for col, mean_val in means.items():
        print(f"{col}: {mean_val:.2f}")
    plot_bar_chart(means)
