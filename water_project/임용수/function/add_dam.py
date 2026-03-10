import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import numpy as np

class Add_Dam():
    def _prepare_date_columns(self, water_df, dam_df):
        """데이터 복사 및 날짜 형식 변환"""
        water_df = water_df.copy()
        # index가 날짜라고 가정 (원본 코드 유지)
        water_df['일자_dt'] = pd.to_datetime(water_df.index)
        
        dam_df = dam_df.copy()
        dam_df['일자'] = pd.to_datetime(dam_df['일자'])
        
        return water_df, dam_df
    
    def _aggregate_water_monthly(self, water_df):
        """수질 데이터: 연월별 '평균' 집계"""
        water_columns = {
            '수온': 'mean',
            '수소이온농도(ph)':'mean',
            '전기전도도(EC)':'mean',
            '용존산소(DO)':'mean',
            'BOD':'mean',
            'COD':'mean',
            '유량': 'mean',
            '총질소(T-N)':'mean',
            '총유기탄소(TOC)': 'mean',
            '총인(T-P)': 'mean',
            '부유물질': 'mean',
            '클로로필-a': 'mean'
        }
        # 존재하는 컬럼만 선택하여 집계 (에러 방지)
        available_water_cols = {k: v for k, v in water_columns.items() if k in water_df.columns}
        water_monthly = water_df.groupby(water_df['일자_dt'].dt.to_period('M')).agg(available_water_cols).reset_index()
        
        return water_monthly
    
    def _preprocess_dam_data(self, dam_df):
        """댐 데이터 전처리: 월 합계를 '일평균'으로 변환"""
        # 필수 컬럼 확인
        required_cols = ['하굿둑방류량', '하굿둑강수량']
        missing_cols = [col for col in required_cols if col not in dam_df.columns]
        if missing_cols:
            raise ValueError(f"필수 컬럼이 없습니다: {missing_cols}")
        
        # 이미 월별로 한 행씩 있다고 가정하므로 바로 계산
        dam_df['days_in_month'] = dam_df['일자'].dt.daysinmonth
        dam_df['하굿둑방류량_평균'] = dam_df['하굿둑방류량'] / dam_df['days_in_month']
        dam_df['하굿둑강수량_평균'] = dam_df['하굿둑강수량'] / dam_df['days_in_month']
        
        # 병합을 위해 '일자'를 Period 형식으로 통일
        dam_df['일자_period'] = dam_df['일자'].dt.to_period('M')
        
        return dam_df
    
    def _merge_datasets(self, water_monthly, dam_df):
        """두 데이터 병합 (Period 기준)"""
        result = pd.merge(
            water_monthly, 
            dam_df[['일자_period', '하굿둑방류량_평균', '하굿둑강수량_평균']], 
            left_on='일자_dt', 
            right_on='일자_period', 
            how='inner'
        )
        
        if result.empty:
            raise ValueError("병합 결과가 비어있습니다. 데이터의 날짜 범위를 확인하세요.")
        
        return result
    
    def _finalize_result(self, result, new_order=None):
        """최종 정리: Period를 다시 Timestamp로 변환하고 불필요한 컬럼 삭제"""
        if new_order is None:
            new_order = ['일자', '수온', '수소이온농도(ph)', '전기전도도(EC)', '용존산소(DO)', 
                        'BOD', 'COD', '총질소(T-N)', '유량', '총유기탄소(TOC)', '총인(T-P)', 
                        '부유물질', '하굿둑방류량_평균', '하굿둑강수량_평균', '클로로필-a']
        
        # Period를 다시 Timestamp로 변환하고 불필요한 컬럼 삭제
        result['일자'] = result['일자_dt'].dt.to_timestamp()
        result = result.drop(columns=['일자_dt', '일자_period'])
        
        # 정렬 및 결측치 처리
        result = result.sort_values('일자').reset_index(drop=True)
        result.dropna(inplace=True)
        
        # new_order에 있는 컬럼만 선택 (존재하지 않는 컬럼은 무시)
        available_cols = [col for col in new_order if col in result.columns]
        missing_cols = [col for col in new_order if col not in result.columns]
        if missing_cols:
            print(f"경고: 다음 컬럼이 결과에 없습니다: {missing_cols}")
        
        return result.reindex(columns=available_cols)
    
    def month_dam_add(self, water_df, dam_df):
        # 1. 데이터 복사 및 날짜 형식 변환
        water_df, dam_df = self._prepare_date_columns(water_df, dam_df)

        # 2. 수질 데이터: 연월별 '평균' 집계
        water_monthly = self._aggregate_water_monthly(water_df)

        # 3. 댐 데이터 전처리: 월 합계를 '일평균'으로 변환
        dam_df = self._preprocess_dam_data(dam_df)

        # 4. 두 데이터 병합 (Period 기준)
        result = self._merge_datasets(water_monthly, dam_df)

        # 5. 최종 정리: Period를 다시 Timestamp로 변환하고 불필요한 컬럼 삭제
        result = self._finalize_result(result)
        
        return result
    
    def month_dam_add_small(self, water_df, dam_df):
        # 1. 데이터 복사 및 날짜 형식 변환
        water_df, dam_df = self._prepare_date_columns(water_df, dam_df)

        # 2. 수질 데이터: 연월별 '평균' 집계
        water_monthly = self._aggregate_water_monthly(water_df)

        # 3. 댐 데이터 전처리: 월 합계를 '일평균'으로 변환
        dam_df = self._preprocess_dam_data(dam_df)

        # 4. 두 데이터 병합 (Period 기준)
        result = self._merge_datasets(water_monthly, dam_df)

        # 5. 최종 정리: Period를 다시 Timestamp로 변환하고 불필요한 컬럼 삭제
        result = self._finalize_result(result, new_order=[
            '일자',
            '수온', 
            '하굿둑방류량_평균', 
            '총인(T-P)', 
            '총질소(T-N)', 
            '하굿둑강수량_평균', 
            '클로로필-a'  # Target
        ])
        
        return result
    

    def _sort_by_date(self, df):
        """시계열 데이터를 날짜 기준으로 정렬"""
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        return df
    
    def _apply_log_transform(self, df, cols=None):
        """특정 컬럼에 로그 변환 적용"""
        if cols is None:
            cols = ['유량', '하굿둑강수량_평균', '하굿둑방류량_평균', '클로로필-a']
        
        df_transformed = df.copy()
        for col in cols:
            if col in df_transformed.columns:
                df_transformed[col] = np.log1p(df_transformed[col])
        
        return df_transformed
    
    def _split_features_target(self, df):
        """독립변수(X)와 종속변수(y) 분리"""
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
        return X, y
    
    def _scale_features(self, xtrain, xtest):
        """특성 스케일링"""
        sc = StandardScaler()
        xtrain_scaled = pd.DataFrame(
            sc.fit_transform(xtrain), 
            columns=xtrain.columns, 
            index=xtrain.index
        )
        xtest_scaled = pd.DataFrame(
            sc.transform(xtest), 
            columns=xtest.columns, 
            index=xtest.index
        )
        return xtrain_scaled, xtest_scaled
    
    def log_scale(self, df, test_size=0.2, log_cols=None):
        """
        데이터 로그 변환, 분할, 스케일링 수행
        
        Parameters:
        -----------
        df : pd.DataFrame
            입력 데이터프레임
        test_size : float, default=0.2
            테스트 데이터 비율
        log_cols : list, optional
            로그 변환할 컬럼 리스트 (기본값: ['유량', '하굿둑강수량_평균', '하굿둑방류량_평균', '클로로필-a'])
        
        Returns:
        --------
        xtrain_scaled, xtest_scaled, ytrain, ytest
        """
        # 1. 시계열 순서대로 정렬
        df = self._sort_by_date(df)

        # 2. 특정 컬럼 로그 변환
        df_transformed = self._apply_log_transform(df, log_cols)

        # 3. 독립변수(X)와 종속변수(y) 분리
        X, y = self._split_features_target(df_transformed)

        # 4. 시계열 데이터 분할 (순서 유지)
        xtrain, xtest, ytrain, ytest = train_test_split(
            X, y, 
            test_size=test_size, 
            shuffle=False  # 시계열 데이터이므로 순서 섞지 않음
        )

        # 5. 스케일링
        xtrain_scaled, xtest_scaled = self._scale_features(xtrain, xtest)

        return xtrain_scaled, xtest_scaled, ytrain, ytest
    
    