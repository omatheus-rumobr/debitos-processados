from sqlalchemy import create_engine, Column, Integer, String, Numeric, Boolean, Text, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List, Dict, Any
from os import getenv
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class Cte(Base):
    """
    Modelo SQLAlchemy para a tabela cte
    """
    __tablename__ = 'cte'

    id_cte = Column(Integer, primary_key=True, autoincrement=True)
    nr_doc = Column(Integer, nullable=False)
    nr_serie = Column(Integer, nullable=False)
    tp_modelo = Column(String(2), nullable=False)
    dt_cancelamento = Column(String(45), nullable=True)
    dt_emissao = Column(DateTime, nullable=False)
    nr_cnpj = Column(String(14), nullable=False)
    nm_pessoa_pagador = Column(String(255), nullable=False)
    nr_cnpj_cpf_pagador = Column(String(14), nullable=False)
    nr_cnpj_cpf_pagador_raiz = Column(String(8), nullable=False)
    vl_total = Column(Numeric(11, 2), nullable=False)
    vl_pedagio = Column(Numeric(11, 2), nullable=False)
    vl_recebido = Column(Numeric(11, 2), nullable=False)
    in_exportacao = Column(Boolean, default=False, nullable=False)
    in_pe = Column(Boolean, default=False, nullable=False)
    tp_destino = Column(Text, default='N', nullable=False)
    nr_chave_nfe = Column(String(54), nullable=False)
    nr_chave_cte = Column(String(45), nullable=False)
    cd_mun_orig = Column(Integer, nullable=False)
    cd_mun_dest = Column(Integer, nullable=False)
    cd_cfop = Column(String(4), nullable=True)
    id_arquivo = Column(Integer, ForeignKey('arquivo.id_arquivo'), nullable=False)
    id_transportador = Column(Integer, nullable=False)
    id_totalizacao = Column(Integer, nullable=True)
    tp_totalizacao = Column(String(2), nullable=True)
    id_utilizacao = Column(Integer, ForeignKey('utilizacao.id_utilizacao'), nullable=True)
    nr_cnpj_remetente = Column(String(14), nullable=False)
    nr_cnpj_expedidor = Column(String(14), nullable=False)
    nr_cnpj_destinatario = Column(String(14), nullable=False)
    nr_cnpj_recebedor = Column(String(14), nullable=False)
    cd_mun_remetente = Column(Integer, nullable=True)
    cd_mun_expedidor = Column(Integer, nullable=True)
    cd_mun_destinatario = Column(Integer, nullable=True)
    cd_mun_recebedor = Column(Integer, nullable=True)
    tp_cte = Column(String(1), nullable=True)
    dt_anulacao = Column(Date, nullable=True)
    nr_chave_cte_ref = Column(String(44), nullable=True)
    dt_emissao_anulacao = Column(Date, nullable=True)
    vl_receber = Column(Numeric(11, 2), default=0, nullable=False)
    id_user_considerou = Column(Integer, nullable=True)
    motivo_consideracao = Column(String(191), nullable=True)
    dt_consideracao = Column(DateTime, nullable=True)
    nr_nfe_anulacao = Column(Integer, nullable=True)
    nr_ie_remetente = Column(String(14), nullable=True)
    nr_ie_destinatario = Column(String(14), nullable=True)
    nr_ie_recebedor = Column(String(14), nullable=True)
    nr_ie_expedidor = Column(String(14), nullable=True)
    is_produtor_rural = Column(Boolean, default=False, nullable=False)
    nr_chave_cte_anterior = Column(String(191), nullable=True)
    tx_observacao = Column(Text, nullable=True)
    nm_produto_principal = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    consulta_manual = Column(Boolean, default=False, nullable=False)
    inf_fisco = Column(Text, nullable=True)
    inf_doc_outros = Column(String(1), nullable=True)
    tp_servico = Column(String(191), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            'id_transportador', 'nr_cnpj', 'nr_doc', 'nr_serie', 'tp_modelo',
            name='cte_id_transportador_nr_cnpj_nr_doc_nr_serie_tp_modelo_unique'
        ),
    )

    def __repr__(self):
        return f"<Cte(id_cte={self.id_cte}, nr_chave_cte='{self.nr_chave_cte}', nr_doc={self.nr_doc})>"

    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto Cte para um dicionário"""
        return {
            'id_cte': self.id_cte,
            'nr_doc': self.nr_doc,
            'nr_serie': self.nr_serie,
            'tp_modelo': self.tp_modelo,
            'dt_cancelamento': self.dt_cancelamento,
            'dt_emissao': self.dt_emissao.isoformat() if self.dt_emissao else None,
            'nr_cnpj': self.nr_cnpj,
            'nm_pessoa_pagador': self.nm_pessoa_pagador,
            'nr_cnpj_cpf_pagador': self.nr_cnpj_cpf_pagador,
            'nr_cnpj_cpf_pagador_raiz': self.nr_cnpj_cpf_pagador_raiz,
            'vl_total': float(self.vl_total) if self.vl_total else None,
            'vl_pedagio': float(self.vl_pedagio) if self.vl_pedagio else None,
            'vl_recebido': float(self.vl_recebido) if self.vl_recebido else None,
            'in_exportacao': self.in_exportacao,
            'in_pe': self.in_pe,
            'tp_destino': self.tp_destino,
            'nr_chave_nfe': self.nr_chave_nfe,
            'nr_chave_cte': self.nr_chave_cte,
            'cd_mun_orig': self.cd_mun_orig,
            'cd_mun_dest': self.cd_mun_dest,
            'cd_cfop': self.cd_cfop,
            'id_arquivo': self.id_arquivo,
            'id_transportador': self.id_transportador,
            'id_totalizacao': self.id_totalizacao,
            'tp_totalizacao': self.tp_totalizacao,
            'id_utilizacao': self.id_utilizacao,
            'nr_cnpj_remetente': self.nr_cnpj_remetente,
            'nr_cnpj_expedidor': self.nr_cnpj_expedidor,
            'nr_cnpj_destinatario': self.nr_cnpj_destinatario,
            'nr_cnpj_recebedor': self.nr_cnpj_recebedor,
            'cd_mun_remetente': self.cd_mun_remetente,
            'cd_mun_expedidor': self.cd_mun_expedidor,
            'cd_mun_destinatario': self.cd_mun_destinatario,
            'cd_mun_recebedor': self.cd_mun_recebedor,
            'tp_cte': self.tp_cte,
            'dt_anulacao': self.dt_anulacao.isoformat() if self.dt_anulacao else None,
            'nr_chave_cte_ref': self.nr_chave_cte_ref,
            'dt_emissao_anulacao': self.dt_emissao_anulacao.isoformat() if self.dt_emissao_anulacao else None,
            'vl_receber': float(self.vl_receber) if self.vl_receber else None,
            'id_user_considerou': self.id_user_considerou,
            'motivo_consideracao': self.motivo_consideracao,
            'dt_consideracao': self.dt_consideracao.isoformat() if self.dt_consideracao else None,
            'nr_nfe_anulacao': self.nr_nfe_anulacao,
            'nr_ie_remetente': self.nr_ie_remetente,
            'nr_ie_destinatario': self.nr_ie_destinatario,
            'nr_ie_recebedor': self.nr_ie_recebedor,
            'nr_ie_expedidor': self.nr_ie_expedidor,
            'is_produtor_rural': self.is_produtor_rural,
            'nr_chave_cte_anterior': self.nr_chave_cte_anterior,
            'tx_observacao': self.tx_observacao,
            'nm_produto_principal': self.nm_produto_principal,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'consulta_manual': self.consulta_manual,
            'inf_fisco': self.inf_fisco,
            'inf_doc_outros': self.inf_doc_outros,
            'tp_servico': self.tp_servico,
        }


class CteCRUD:
    """
    Classe para operações CRUD na tabela cte
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Inicializa a conexão com o banco de dados
        
        Args:
            database_url: URL de conexão do banco de dados PostgreSQL
                         Formato: postgresql://usuario:senha@host:porta/nome_banco
                         Se None, tenta obter das variáveis de ambiente
        """
        if database_url is None:
            db_user = getenv('DB_USER', 'postgres')
            db_password = getenv('DB_PASSWORD', '')
            db_host = getenv('DB_HOST', 'localhost')
            db_port = getenv('DB_PORT', '5432')
            db_name = getenv('DB_NAME', 'postgres')
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
    
    def get_session(self) -> Session:
        """Retorna uma nova sessão do banco de dados"""
        return self.SessionLocal()
    
    # CREATE
    def create(self, cte_data: Dict[str, Any]) -> Cte:
        """
        Cria um novo registro de CTE
        
        Args:
            cte_data: Dicionário com os dados do CTE
        
        Returns:
            Objeto Cte criado
        
        Raises:
            Exception: Se houver erro ao criar o registro
        """
        session = self.get_session()
        try:
            cte = Cte(**cte_data)
            session.add(cte)
            session.commit()
            session.refresh(cte)
            return cte
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro ao criar CTE: {str(e)}")
        finally:
            session.close()
    
    def create_bulk(self, ctes_data: List[Dict[str, Any]]) -> List[Cte]:
        """
        Cria múltiplos registros de CTE de uma vez
        
        Args:
            ctes_data: Lista de dicionários com os dados dos CTEs
        
        Returns:
            Lista de objetos Cte criados
        
        Raises:
            Exception: Se houver erro ao criar os registros
        """
        session = self.get_session()
        try:
            ctes = [Cte(**cte_data) for cte_data in ctes_data]
            session.add_all(ctes)
            session.commit()
            for cte in ctes:
                session.refresh(cte)
            return ctes
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro ao criar CTEs em lote: {str(e)}")
        finally:
            session.close()
    
    # READ
    def get_by_id(self, id_cte: int) -> Optional[Cte]:
        """
        Busca um CTE pelo ID
        
        Args:
            id_cte: ID do CTE
        
        Returns:
            Objeto Cte ou None se não encontrado
        """
        session = self.get_session()
        try:
            return session.query(Cte).filter(Cte.id_cte == id_cte).first()
        finally:
            session.close()
    
    def get_by_chave_cte(self, nr_chave_cte: str, id_transportador: Optional[int] = None) -> Optional[Cte]:
        """
        Busca um CTE pela chave do CTE
        
        Args:
            nr_chave_cte: Número da chave do CTE
            id_transportador: ID do transportador (opcional, para melhorar performance)
        
        Returns:
            Objeto Cte ou None se não encontrado
        """
        session = self.get_session()
        try:
            query = session.query(Cte).filter(Cte.nr_chave_cte == nr_chave_cte)
            if id_transportador:
                query = query.filter(Cte.id_transportador == id_transportador)
            return query.first()
        finally:
            session.close()
    
    def get_by_chave_nfe(self, nr_chave_nfe: str, id_transportador: Optional[int] = None) -> Optional[Cte]:
        """
        Busca um CTE pela chave da NFE
        
        Args:
            nr_chave_nfe: Número da chave da NFE
            id_transportador: ID do transportador (opcional, para melhorar performance)
        
        Returns:
            Objeto Cte ou None se não encontrado
        """
        session = self.get_session()
        try:
            query = session.query(Cte).filter(Cte.nr_chave_nfe == nr_chave_nfe)
            if id_transportador:
                query = query.filter(Cte.id_transportador == id_transportador)
            return query.first()
        finally:
            session.close()
    
    def get_campos_por_chave_cte(self, nr_chave_cte: str) -> Optional[Dict[str, Any]]:
        """
        Busca campos específicos de um CTE pela chave do CTE
        
        Retorna os seguintes campos:
        - cd_mun_orig
        - cd_mun_dest
        - vl_total
        - nr_cnpj_cpf_pagador
        - nm_pessoa_pagador
        - in_exportacao
        - tp_destino
        - nr_chave_nfe
        - nr_chave_cte
        
        Args:
            nr_chave_cte: Número da chave do CTE
        
        Returns:
            Dicionário com os campos solicitados ou None se não encontrado
        """
        session = self.get_session()
        try:
            cte = session.query(Cte).filter(Cte.nr_chave_cte == nr_chave_cte).first()
            if not cte:
                return None
            
            return {
                'cd_mun_orig': cte.cd_mun_orig,
                'cd_mun_dest': cte.cd_mun_dest,
                'vl_total': float(cte.vl_total) if cte.vl_total else None,
                'nr_cnpj_cpf_pagador': cte.nr_cnpj_cpf_pagador,
                'nm_pessoa_pagador': cte.nm_pessoa_pagador,
                'in_exportacao': cte.in_exportacao,
                'tp_destino': cte.tp_destino,
                'nr_chave_nfe': cte.nr_chave_nfe,
                'nr_chave_cte': cte.nr_chave_cte
            }
        finally:
            session.close()
    
    def get_ids_by_chaves_cte(self, chaves_cte: tuple) -> List[Dict[str, Any]]:
        """
        Busca campos específicos dos CTEs baseado em uma tupla de chaves CTE
        
        Equivalente à query SQL:
        SELECT c.cd_mun_orig, c.cd_mun_dest, c.vl_total, c.nr_cnpj_cpf_pagador, 
               c.nm_pessoa_pagador, c.in_exportacao, c.tp_destino, c.nr_chave_nfe, 
               c.nr_chave_cte 
        FROM cte c 
        WHERE c.nr_chave_cte IN (...)
        
        Args:
            chaves_cte: Tupla ou lista com as chaves CTE a serem buscadas
        
        Returns:
            Lista de dicionários com os campos solicitados dos CTEs encontrados
        """
        session = self.get_session()
        try:
            if not chaves_cte:
                return []
            
            resultados = session.query(
                Cte.cd_mun_orig,
                Cte.cd_mun_dest,
                Cte.vl_total,
                Cte.nr_cnpj_cpf_pagador,
                Cte.nm_pessoa_pagador,
                Cte.in_exportacao,
                Cte.tp_destino,
                Cte.nr_chave_nfe,
                Cte.nr_chave_cte,
                Cte.nr_doc,
                Cte.nr_chave_cte_anterior
            ).filter(
                Cte.nr_chave_cte.in_(chaves_cte)
            ).all()
            
            return [
                {
                    'cd_mun_orig': r[0],
                    'cd_mun_dest': r[1],
                    'vl_total': float(r[2]) if r[2] else None,
                    'nr_cnpj_cpf_pagador': r[3],
                    'nm_pessoa_pagador': r[4],
                    'in_exportacao': r[5],
                    'tp_destino': r[6],
                    'nr_chave_nfe': r[7],
                    'nr_chave_cte': r[8],
                    'nr_doc': r[9],
                    'nr_chave_cte_anterior': r[10]
                }
                for r in resultados
            ]
        finally:
            session.close()
    
    def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        id_transportador: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Cte]:
        """
        Busca todos os CTEs com filtros opcionais
        
        Args:
            limit: Limite de registros a retornar
            offset: Número de registros a pular
            id_transportador: Filtrar por ID do transportador
            filters: Dicionário com filtros adicionais (ex: {'nr_doc': 123, 'tp_modelo': '57'})
        
        Returns:
            Lista de objetos Cte
        """
        session = self.get_session()
        try:
            query = session.query(Cte)
            
            if id_transportador:
                query = query.filter(Cte.id_transportador == id_transportador)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(Cte, key):
                        query = query.filter(getattr(Cte, key) == value)
            
            if offset:
                query = query.offset(offset)
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        finally:
            session.close()
    
    def count(self, id_transportador: Optional[int] = None, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Conta o número de CTEs com filtros opcionais
        
        Args:
            id_transportador: Filtrar por ID do transportador
            filters: Dicionário com filtros adicionais
        
        Returns:
            Número total de registros
        """
        session = self.get_session()
        try:
            query = session.query(Cte)
            
            if id_transportador:
                query = query.filter(Cte.id_transportador == id_transportador)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(Cte, key):
                        query = query.filter(getattr(Cte, key) == value)
            
            return query.count()
        finally:
            session.close()
    
    # UPDATE
    def update(self, id_cte: int, update_data: Dict[str, Any]) -> Optional[Cte]:
        """
        Atualiza um CTE existente
        
        Args:
            id_cte: ID do CTE a ser atualizado
            update_data: Dicionário com os campos a serem atualizados
        
        Returns:
            Objeto Cte atualizado ou None se não encontrado
        
        Raises:
            Exception: Se houver erro ao atualizar o registro
        """
        session = self.get_session()
        try:
            cte = session.query(Cte).filter(Cte.id_cte == id_cte).first()
            if not cte:
                return None
            
            for key, value in update_data.items():
                if hasattr(cte, key):
                    setattr(cte, key, value)
            
            session.commit()
            session.refresh(cte)
            return cte
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro ao atualizar CTE: {str(e)}")
        finally:
            session.close()
    
    def update_by_chave_cte(
        self,
        nr_chave_cte: str,
        update_data: Dict[str, Any],
        id_transportador: Optional[int] = None
    ) -> Optional[Cte]:
        """
        Atualiza um CTE pela chave do CTE
        
        Args:
            nr_chave_cte: Número da chave do CTE
            update_data: Dicionário com os campos a serem atualizados
            id_transportador: ID do transportador (opcional)
        
        Returns:
            Objeto Cte atualizado ou None se não encontrado
        
        Raises:
            Exception: Se houver erro ao atualizar o registro
        """
        session = self.get_session()
        try:
            query = session.query(Cte).filter(Cte.nr_chave_cte == nr_chave_cte)
            if id_transportador:
                query = query.filter(Cte.id_transportador == id_transportador)
            
            cte = query.first()
            if not cte:
                return None
            
            for key, value in update_data.items():
                if hasattr(cte, key):
                    setattr(cte, key, value)
            
            session.commit()
            session.refresh(cte)
            return cte
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro ao atualizar CTE: {str(e)}")
        finally:
            session.close()
    
    # DELETE
    def delete(self, id_cte: int) -> bool:
        """
        Deleta um CTE pelo ID
        
        Args:
            id_cte: ID do CTE a ser deletado
        
        Returns:
            True se deletado com sucesso, False se não encontrado
        
        Raises:
            Exception: Se houver erro ao deletar o registro
        """
        session = self.get_session()
        try:
            cte = session.query(Cte).filter(Cte.id_cte == id_cte).first()
            if not cte:
                return False
            
            session.delete(cte)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro ao deletar CTE: {str(e)}")
        finally:
            session.close()
    
    def delete_by_chave_cte(
        self,
        nr_chave_cte: str,
        id_transportador: Optional[int] = None
    ) -> bool:
        """
        Deleta um CTE pela chave do CTE
        
        Args:
            nr_chave_cte: Número da chave do CTE
            id_transportador: ID do transportador (opcional)
        
        Returns:
            True se deletado com sucesso, False se não encontrado
        
        Raises:
            Exception: Se houver erro ao deletar o registro
        """
        session = self.get_session()
        try:
            query = session.query(Cte).filter(Cte.nr_chave_cte == nr_chave_cte)
            if id_transportador:
                query = query.filter(Cte.id_transportador == id_transportador)
            
            cte = query.first()
            if not cte:
                return False
            
            session.delete(cte)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro ao deletar CTE: {str(e)}")
        finally:
            session.close()
    
    def exists(
        self,
        id_transportador: int,
        nr_cnpj: str,
        nr_doc: int,
        nr_serie: int,
        tp_modelo: str
    ) -> bool:
        """
        Verifica se um CTE já existe baseado na constraint única
        
        Args:
            id_transportador: ID do transportador
            nr_cnpj: Número do CNPJ
            nr_doc: Número do documento
            nr_serie: Número da série
            tp_modelo: Tipo do modelo
        
        Returns:
            True se existe, False caso contrário
        """
        session = self.get_session()
        try:
            count = session.query(Cte).filter(
                Cte.id_transportador == id_transportador,
                Cte.nr_cnpj == nr_cnpj,
                Cte.nr_doc == nr_doc,
                Cte.nr_serie == nr_serie,
                Cte.tp_modelo == tp_modelo
            ).count()
            return count > 0
        finally:
            session.close()


# Exemplo de uso
if __name__ == "__main__":
    # Inicializar o CRUD
    crud = CteCRUD()
    
    # Exemplo de criação
    novo_cte = {
        'nr_doc': 123456,
        'nr_serie': 1,
        'tp_modelo': '57',
        'dt_emissao': datetime.now(),
        'nr_cnpj': '12345678000190',
        'nm_pessoa_pagador': 'Empresa Exemplo',
        'nr_cnpj_cpf_pagador': '12345678000190',
        'nr_cnpj_cpf_pagador_raiz': '12345678',
        'vl_total': 1000.00,
        'vl_pedagio': 50.00,
        'vl_recebido': 1000.00,
        'nr_chave_nfe': '35201212345678000190570000001234567890123456',
        'nr_chave_cte': '35201212345678000190570000001234567890123456',
        'cd_mun_orig': 3550308,
        'cd_mun_dest': 3550308,
        'id_arquivo': 1,
        'id_transportador': 1,
        'nr_cnpj_remetente': '12345678000190',
        'nr_cnpj_expedidor': '12345678000190',
        'nr_cnpj_destinatario': '12345678000190',
        'nr_cnpj_recebedor': '12345678000190',
    }
    
    # Criar CTE
    # cte_criado = crud.create(novo_cte)
    # print(f"CTE criado: {cte_criado}")
    
    # Buscar por ID
    # cte = crud.get_by_id(1)
    # print(f"CTE encontrado: {cte}")
    
    # Atualizar
    # cte_atualizado = crud.update(1, {'vl_total': 1500.00})
    # print(f"CTE atualizado: {cte_atualizado}")
    
    # Deletar
    # deletado = crud.delete(1)
    # print(f"CTE deletado: {deletado}")
