# Ansible vs Jenkins 비교 가이드

## 핵심 차이

```
Ansible: 설정 관리 및 배포 자동화 도구
Jenkins: CI/CD 파이프라인 및 빌드 자동화 도구
```

**결론**: 목적이 다르며, 보통 함께 사용합니다.

## 상세 비교

| 항목 | Ansible | Jenkins |
|------|---------|---------|
| 주요 목적 | 인프라 자동화, 서버 설정 | CI/CD 파이프라인, 빌드 자동화 |
| 실행 방식 | Push (명령 실행) | Pull (트리거 기반) |
| 에이전트 | 불필요 (SSH 사용) | 필요 (Jenkins Agent) |
| 설정 언어 | YAML | Groovy (Pipeline) |
| 학습 곡선 | 쉬움 | 중간 |
| GUI | 없음 (CLI 기반) | 있음 (Web UI) |
| 상태 관리 | 멱등성 보장 | 파이프라인 상태 관리 |
| Git 연동 | 수동 | 자동 (Webhook, Polling) |
| 히스토리 | 제한적 | 완전한 빌드 히스토리 |

## 사용 시나리오

### Ansible이 적합한 경우

**인프라 설정 및 관리:**
- 패키지 설치 및 업데이트
- 설정 파일 배포
- 사용자 및 권한 관리
- 방화벽 설정
- 서비스 시작/중지/재시작

**애플리케이션 배포:**
- 파일 복사 및 배포
- 스크립트 실행
- 데이터베이스 마이그레이션
- 여러 서버 동시 배포

**예시:**
```yaml
# deploy.yml
---
- name: Deploy backup tool
  hosts: all
  tasks:
    - name: Copy script
      copy:
        src: backup.py
        dest: /opt/backup.py
    
    - name: Install packages
      pip:
        requirements: requirements.txt
    
    - name: Start service
      systemd:
        name: backup
        state: started
```

### Jenkins가 적합한 경우

**CI/CD 파이프라인:**
- Git 커밋 시 자동 빌드
- 자동 테스트 실행
- 코드 품질 검사 (SonarQube 등)
- 빌드 아티팩트 생성
- 배포 승인 프로세스
- 스케줄 기반 작업

**자동화 워크플로우:**
- 다단계 배포 (Dev → Staging → Prod)
- 알림 (Slack, Email)
- 빌드 히스토리 관리
- 롤백 기능

**예시:**
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'python -m pytest'
            }
        }
        
        stage('Deploy') {
            steps {
                sh 'scp backup.py user@server:/opt/'
            }
        }
    }
}
```

## 실전 사용 패턴

### 패턴 1: Ansible만 사용 (소규모)

**적합한 상황:**
- 팀 규모: 1-5명
- 배포 빈도: 주 1회 이하
- 서버 수: 10대 이하
- 간단한 배포 프로세스

**워크플로우:**
```bash
# 1. 코드 수정
vim backup.py

# 2. Git push
git commit -am "Update script"
git push

# 3. 수동 배포
ansible-playbook -i inventory.ini deploy.yml
```

**장점:**
- 설정 간단
- 학습 쉬움
- 빠른 시작
- 추가 인프라 불필요

**단점:**
- 수동 실행 필요
- Git 연동 없음
- 히스토리 관리 어려움
- 승인 프로세스 없음

### 패턴 2: Jenkins만 사용

**적합한 상황:**
- 빌드가 필요한 프로젝트 (Java, Go 등)
- 복잡한 테스트 파이프라인
- 간단한 배포 (단일 서버)

**워크플로우:**
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
        
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
        
        stage('Deploy') {
            steps {
                sh '''
                    scp backup.py user@server:/opt/
                    ssh user@server "systemctl restart backup"
                '''
            }
        }
    }
}
```

**장점:**
- 완전 자동화
- Git 연동
- 빌드 히스토리
- Web UI

**단점:**
- 복잡한 서버 설정 어려움
- 여러 서버 배포 복잡
- SSH 키 관리 번거로움

### 패턴 3: Jenkins + Ansible (권장, 중대규모)

**적합한 상황:**
- 팀 규모: 5명 이상
- 배포 빈도: 주 여러 번
- 서버 수: 10대 이상
- 여러 환경 (Dev, Staging, Prod)
- 승인 프로세스 필요

**프로젝트 구조:**
```
backup-tool/
├── backup.py
├── requirements.txt
├── tests/
│   └── test_backup.py
├── ansible/
│   ├── inventory/
│   │   ├── dev.ini
│   │   ├── staging.ini
│   │   └── prod.ini
│   ├── deploy.yml
│   ├── test.yml
│   └── templates/
│       └── config.yaml.j2
├── Jenkinsfile
└── README.md
```

**Jenkinsfile:**
```groovy
pipeline {
    agent any
    
    triggers {
        pollSCM('H/5 * * * *')  // 5분마다 Git 체크
    }
    
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/company/backup-tool.git'
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install -r requirements.txt
                    python -m pytest tests/
                '''
            }
        }
        
        stage('Deploy to Dev') {
            steps {
                sh 'ansible-playbook -i ansible/inventory/dev.ini ansible/deploy.yml'
            }
        }
        
        stage('Integration Test') {
            steps {
                sh 'ansible-playbook -i ansible/inventory/dev.ini ansible/test.yml'
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                sh 'ansible-playbook -i ansible/inventory/staging.ini ansible/deploy.yml'
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                sh 'ansible-playbook -i ansible/inventory/prod.ini ansible/deploy.yml'
            }
        }
    }
    
    post {
        success {
            slackSend color: 'good', message: "✅ Deployed successfully: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
        failure {
            slackSend color: 'danger', message: "❌ Deployment failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
        always {
            cleanWs()
        }
    }
}
```

**Ansible Playbook (deploy.yml):**
```yaml
---
- name: Deploy backup tool
  hosts: all
  become: yes
  vars:
    install_dir: /opt/backup-tool
    venv_dir: "{{ install_dir }}/venv"
  
  tasks:
    - name: Create installation directory
      file:
        path: "{{ install_dir }}"
        state: directory
        mode: '0755'
    
    - name: Copy backup script
      copy:
        src: ../../backup.py
        dest: "{{ install_dir }}/backup.py"
        mode: '0755'
    
    - name: Copy requirements
      copy:
        src: ../../requirements.txt
        dest: "{{ install_dir }}/requirements.txt"
    
    - name: Create virtual environment
      command: python3 -m venv {{ venv_dir }}
      args:
        creates: "{{ venv_dir }}/bin/activate"
    
    - name: Install packages
      pip:
        requirements: "{{ install_dir }}/requirements.txt"
        virtualenv: "{{ venv_dir }}"
    
    - name: Deploy config
      template:
        src: templates/config.yaml.j2
        dest: "{{ install_dir }}/config.yaml"
    
    - name: Create systemd service
      template:
        src: templates/backup.service.j2
        dest: /etc/systemd/system/backup.service
      notify: Reload systemd
    
    - name: Enable and start service
      systemd:
        name: backup
        enabled: yes
        state: started
  
  handlers:
    - name: Reload systemd
      systemd:
        daemon_reload: yes
```

**워크플로우:**
```bash
# 1. 개발자가 코드 수정
vim backup.py

# 2. Git push
git commit -am "Update backup logic"
git push origin develop

# 3. Jenkins가 자동으로:
#    ✓ Git 변경 감지
#    ✓ 테스트 실행
#    ✓ Dev 환경 배포 (Ansible)
#    ✓ 통합 테스트
#    ✓ Staging 배포 (develop 브랜치)
#    ✓ Slack 알림

# 4. Production 배포 (main 브랜치)
git checkout main
git merge develop
git push origin main

# 5. Jenkins가:
#    ✓ 승인 대기
#    ✓ (승인 후) Prod 배포 (Ansible)
#    ✓ Slack 알림
```

**장점:**
- 완전 자동화 (Git push → 자동 배포)
- Jenkins의 파이프라인 관리
- Ansible의 강력한 배포 기능
- 승인 프로세스
- 히스토리 관리
- 알림 (Slack, Email)
- 롤백 가능

**단점:**
- 초기 설정 복잡
- Jenkins 서버 필요
- 학습 곡선

## 역할 분담

### Jenkins의 역할 (오케스트레이션)

```
✓ Git 변경 감지
✓ 빌드 트리거
✓ 테스트 실행
✓ 파이프라인 관리
✓ 승인 프로세스
✓ 알림 발송
✓ 히스토리 관리
```

### Ansible의 역할 (실제 배포)

```
✓ 서버 설정
✓ 패키지 설치
✓ 파일 배포
✓ 서비스 관리
✓ 여러 서버 동시 처리
✓ 멱등성 보장
```

## 선택 가이드

### Ansible만 사용

```
✅ 사용 조건:
- 소규모 팀 (1-5명)
- 낮은 배포 빈도 (주 1회 이하)
- 적은 서버 수 (10대 이하)
- 간단한 배포 프로세스
- 빠른 시작 필요

✅ 장점:
- 설정 간단
- 학습 쉬움
- 추가 인프라 불필요

❌ 단점:
- 수동 실행
- Git 연동 없음
- 히스토리 관리 어려움
```

### Jenkins + Ansible 사용

```
✅ 사용 조건:
- 중대규모 팀 (5명 이상)
- 높은 배포 빈도 (주 여러 번)
- 많은 서버 수 (10대 이상)
- 여러 환경 (Dev, Staging, Prod)
- 승인 프로세스 필요
- 완전 자동화 필요

✅ 장점:
- 완전 자동화
- Git 연동
- 승인 프로세스
- 히스토리 관리
- 알림 기능
- 롤백 가능

❌ 단점:
- 초기 설정 복잡
- Jenkins 서버 필요
- 학습 시간 필요
```

## 실전 예시: 백업 스크립트 배포

### 시나리오 1: Ansible만 (소규모)

```bash
# 배포
ansible-playbook -i inventory.ini deploy.yml

# 업데이트
ansible-playbook -i inventory.ini deploy.yml

# 롤백
git checkout v1.0.0
ansible-playbook -i inventory.ini deploy.yml
```

### 시나리오 2: Jenkins + Ansible (중대규모)

```
1. 개발자가 feature 브랜치에서 작업
2. Pull Request 생성
3. Jenkins가 자동으로 테스트 실행
4. 리뷰 후 develop 브랜치에 merge
5. Jenkins가 자동으로 Dev 환경 배포
6. QA 테스트
7. main 브랜치에 merge
8. Jenkins가 승인 요청
9. 승인 후 Production 배포
10. Slack 알림
```

## 마이그레이션 경로

### 단계 1: Ansible로 시작

```bash
# 간단한 배포 자동화
ansible-playbook deploy.yml
```

### 단계 2: Jenkins 추가 (수동 트리거)

```groovy
// Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                sh 'ansible-playbook deploy.yml'
            }
        }
    }
}
```

### 단계 3: Git 연동 추가

```groovy
pipeline {
    agent any
    triggers {
        pollSCM('H/5 * * * *')
    }
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/company/backup-tool.git'
            }
        }
        stage('Deploy') {
            steps {
                sh 'ansible-playbook deploy.yml'
            }
        }
    }
}
```

### 단계 4: 테스트 및 승인 추가

```groovy
pipeline {
    agent any
    triggers {
        pollSCM('H/5 * * * *')
    }
    stages {
        stage('Test') {
            steps {
                sh 'python -m pytest'
            }
        }
        stage('Deploy to Dev') {
            steps {
                sh 'ansible-playbook -i inventory/dev.ini deploy.yml'
            }
        }
        stage('Approval') {
            steps {
                input 'Deploy to Production?'
            }
        }
        stage('Deploy to Prod') {
            steps {
                sh 'ansible-playbook -i inventory/prod.ini deploy.yml'
            }
        }
    }
}
```

## 핵심 정리

**Ansible:**
- 서버 설정 및 배포 도구
- SSH 기반, 에이전트 불필요
- YAML로 작성
- 멱등성 보장
- "어떻게 배포할 것인가"

**Jenkins:**
- CI/CD 파이프라인 도구
- Git 연동, 자동 트리거
- 빌드, 테스트, 배포 자동화
- Web UI, 히스토리 관리
- "언제, 무엇을 배포할 것인가"

**함께 사용:**
- Jenkins: 파이프라인 관리 및 오케스트레이션
- Ansible: 실제 배포 수행
- 최고의 조합

**추천:**
- 소규모/간단: Ansible만
- 중대규모/복잡: Jenkins + Ansible

## 참고 자료

- Ansible 공식 문서: https://docs.ansible.com
- Jenkins 공식 문서: https://www.jenkins.io/doc
- Ansible Galaxy (공유 Role): https://galaxy.ansible.com
- Jenkins Plugins: https://plugins.jenkins.io
