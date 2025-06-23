import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database.models import DatabaseManager
from typing import Dict, List

class Dashboard:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def render_user_dashboard(self, user: Dict):
        """Render dashboard for regular users"""
        st.title(f"📊 Dashboard - Selamat datang, {user['full_name'] or user['username']}!")
        
        # Get user stats
        stats = self.db.get_dashboard_stats(user_id=user['id'])
        
        # Stats cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📄 Total Ekstraksi",
                value=stats.get('total_extractions', 0)
            )
        
        with col2:
            st.metric(
                label="✅ Berhasil",
                value=stats.get('successful_extractions', 0)
            )
        
        with col3:
            success_rate = 0
            if stats.get('total_extractions', 0) > 0:
                success_rate = (stats.get('successful_extractions', 0) / stats.get('total_extractions', 1)) * 100
            st.metric(
                label="📈 Tingkat Keberhasilan",
                value=f"{success_rate:.1f}%"
            )
        
        with col4:
            st.metric(
                label="🔄 Aktivitas 7 Hari",
                value=stats.get('recent_activities', 0)
            )
        
        # Recent extractions
        st.subheader("📋 Riwayat Ekstraksi Terbaru")
        history = self.db.get_extraction_history(user_id=user['id'], limit=10)
        
        if history:
            df = pd.DataFrame(history)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['file_size_mb'] = (df['file_size'] / (1024*1024)).round(2)
            
            # Display table
            display_df = df[['filename', 'document_type', 'extraction_status', 'file_size_mb', 'processing_time', 'created_at']].copy()
            display_df.columns = ['Nama File', 'Jenis Dokumen', 'Status', 'Ukuran (MB)', 'Waktu Proses (s)', 'Tanggal']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Chart: Extractions over time
            if len(df) > 1:
                st.subheader("📈 Grafik Ekstraksi")
                
                # Group by date
                df['date'] = df['created_at'].dt.date
                daily_counts = df.groupby('date').size().reset_index(name='count')
                
                fig = px.line(
                    daily_counts, 
                    x='date', 
                    y='count',
                    title='Jumlah Ekstraksi per Hari',
                    labels={'date': 'Tanggal', 'count': 'Jumlah Ekstraksi'}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada riwayat ekstraksi. Mulai dengan mengunggah dokumen!")
        
        # Recent activities
        st.subheader("🔍 Aktivitas Terbaru")
        activities = self.db.get_activity_logs(user_id=user['id'], limit=5)
        
        if activities:
            for activity in activities:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{activity['action']}** - {activity['details']}")
                    with col2:
                        st.caption(activity['created_at'])
                    st.divider()
        else:
            st.info("Belum ada aktivitas yang tercatat.")
    
    def render_admin_dashboard(self, user: Dict):
        """Render dashboard for admin users"""
        st.title(f"👑 Admin Dashboard - {user['full_name'] or user['username']}")
        
        # Get system stats
        stats = self.db.get_dashboard_stats()
        
        # Admin stats cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👥 Total Pengguna",
                value=stats.get('total_users', 0)
            )
        
        with col2:
            st.metric(
                label="📄 Total Ekstraksi",
                value=stats.get('total_extractions', 0)
            )
        
        with col3:
            st.metric(
                label="✅ Ekstraksi Berhasil",
                value=stats.get('successful_extractions', 0)
            )
        
        with col4:
            st.metric(
                label="🔄 Aktivitas 7 Hari",
                value=stats.get('recent_activities', 0)
            )
        
        # Tabs for different admin views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Statistik", "👥 Pengguna", "📋 Riwayat", "🔍 Log Aktivitas"])
        
        with tab1:
            self.render_admin_statistics()
        
        with tab2:
            self.render_user_management()
        
        with tab3:
            self.render_extraction_history()
        
        with tab4:
            self.render_activity_logs()
    
    def render_admin_statistics(self):
        """Render admin statistics"""
        st.subheader("📊 Statistik Sistem")
        
        # Get all extraction history for charts
        history = self.db.get_extraction_history(limit=1000)
        
        if history:
            df = pd.DataFrame(history)
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Document types distribution
                doc_types = df['document_type'].value_counts()
                fig_pie = px.pie(
                    values=doc_types.values,
                    names=doc_types.index,
                    title="Distribusi Jenis Dokumen"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Status distribution
                status_counts = df['extraction_status'].value_counts()
                fig_bar = px.bar(
                    x=status_counts.index,
                    y=status_counts.values,
                    title="Status Ekstraksi",
                    labels={'x': 'Status', 'y': 'Jumlah'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Timeline chart
            df['date'] = df['created_at'].dt.date
            daily_stats = df.groupby(['date', 'extraction_status']).size().reset_index(name='count')
            
            fig_timeline = px.line(
                daily_stats,
                x='date',
                y='count',
                color='extraction_status',
                title='Tren Ekstraksi Harian',
                labels={'date': 'Tanggal', 'count': 'Jumlah'}
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("Belum ada data ekstraksi untuk ditampilkan.")
    
    def render_user_management(self):
        """Render user management interface"""
        st.subheader("👥 Manajemen Pengguna")
        
        # Get all users
        conn = self.db.db_path
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        
        users_df = pd.read_sql_query('''
            SELECT id, username, email, full_name, role, created_at, last_login, is_active
            FROM users
            ORDER BY created_at DESC
        ''', conn)
        conn.close()
        
        if not users_df.empty:
            # Display users table
            st.dataframe(
                users_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "is_active": st.column_config.CheckboxColumn("Aktif"),
                    "created_at": st.column_config.DatetimeColumn("Dibuat"),
                    "last_login": st.column_config.DatetimeColumn("Login Terakhir")
                }
            )
        else:
            st.info("Tidak ada data pengguna.")
    
    def render_extraction_history(self):
        """Render extraction history for admin"""
        st.subheader("📋 Riwayat Ekstraksi Semua Pengguna")
        
        history = self.db.get_extraction_history(limit=50)
        
        if history:
            df = pd.DataFrame(history)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['file_size_mb'] = (df['file_size'] / (1024*1024)).round(2)
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                users = df['username'].unique()
                selected_user = st.selectbox("Filter Pengguna", ['Semua'] + list(users))
            
            with col2:
                doc_types = df['document_type'].unique()
                selected_type = st.selectbox("Filter Jenis Dokumen", ['Semua'] + list(doc_types))
            
            with col3:
                statuses = df['extraction_status'].unique()
                selected_status = st.selectbox("Filter Status", ['Semua'] + list(statuses))
            
            # Apply filters
            filtered_df = df.copy()
            if selected_user != 'Semua':
                filtered_df = filtered_df[filtered_df['username'] == selected_user]
            if selected_type != 'Semua':
                filtered_df = filtered_df[filtered_df['document_type'] == selected_type]
            if selected_status != 'Semua':
                filtered_df = filtered_df[filtered_df['extraction_status'] == selected_status]
            
            # Display filtered data
            display_df = filtered_df[['username', 'filename', 'document_type', 'extraction_status', 'file_size_mb', 'processing_time', 'created_at']].copy()
            display_df.columns = ['Pengguna', 'Nama File', 'Jenis Dokumen', 'Status', 'Ukuran (MB)', 'Waktu Proses (s)', 'Tanggal']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Belum ada riwayat ekstraksi.")
    
    def render_activity_logs(self):
        """Render activity logs for admin"""
        st.subheader("🔍 Log Aktivitas Sistem")
        
        activities = self.db.get_activity_logs(limit=100)
        
        if activities:
            df = pd.DataFrame(activities)
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Filter by action type
            actions = df['action'].unique()
            selected_actions = st.multiselect("Filter Aksi", actions, default=actions)
            
            filtered_df = df[df['action'].isin(selected_actions)]
            
            # Display logs
            for _, activity in filtered_df.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**{activity['action']}**")
                        st.caption(f"User: {activity['username']}")
                    
                    with col2:
                        st.write(activity['details'])
                    
                    with col3:
                        st.caption(activity['created_at'].strftime("%Y-%m-%d %H:%M"))
                    
                    st.divider()
        else:
            st.info("Belum ada log aktivitas.")
