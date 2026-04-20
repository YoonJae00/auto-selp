import pandas as pd

pdata = {
    "상품명": ["테스트 상품 A", "테스트 상품 B"],
    "키워드": ["키워드1", "키워드2"],
    "카테고리ID": ["50001", "50002"]
}
df = pd.DataFrame(pdata)
df.to_excel("test_sample.xlsx", index=False)
