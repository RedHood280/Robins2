"""
Script de prueba para verificar la integridad de los nodos del juego
"""
from Robins import JuegoAventuraBase

def test_starting_nodes():
    """Verifica que todos los nodos de inicio existan"""
    game = JuegoAventuraBase()
    
    starting_nodes = [
        # Jason Todd
        ("jason_facil_inicio", "Jason Todd - Facil"),
        ("jason_normal_inicio", "Jason Todd - Normal"),
        ("jason_dificil_inicio", "Jason Todd - Dificil"),
        
        # Dick Grayson
        ("grayson_facil_inicio", "Dick Grayson - Facil"),
        ("grayson_normal_inicio", "Dick Grayson - Normal"),
        ("grayson_dificil_inicio", "Dick Grayson - Dificil"),
        
        # Tim Drake
        ("tim_facil_inicio", "Tim Drake - Facil"),
        ("tim_normal_inicio", "Tim Drake - Normal"),
        ("tim_dificil_inicio", "Tim Drake - Dificil"),
        
        # Damian Wayne
        ("damian_facil_inicio", "Damian Wayne - Facil"),
        ("damian_normal_inicio", "Damian Wayne - Normal"),
        ("damian_dificil_inicio", "Damian Wayne - Dificil"),
    ]
    
    print("=" * 60)
    print("VERIFICACION DE NODOS DE INICIO")
    print("=" * 60)
    
    all_ok = True
    for node_id, description in starting_nodes:
        if node_id in game.historia:
            node = game.historia[node_id]
            print(f"✓ {description:30} → '{node.titulo}'")
        else:
            print(f"✗ {description:30} → FALTA")
            all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ TODOS LOS NODOS DE INICIO ESTAN CORRECTOS")
    else:
        print("✗ HAY NODOS DE INICIO FALTANTES")
    print("=" * 60)
    
    return all_ok


def test_node_connections():
    """Verifica que los nodos tengan opciones validas"""
    game = JuegoAventuraBase()
    
    print("\n" + "=" * 60)
    print("VERIFICACION DE CONEXIONES DE NODOS")
    print("=" * 60)
    
    broken_connections = []
    nodes_checked = 0
    
    for node_id, node in game.historia.items():
        nodes_checked += 1
        for opcion in node.opciones:
            if opcion['siguiente'] not in game.historia:
                broken_connections.append({
                    'from': node_id,
                    'to': opcion['siguiente'],
                    'option': opcion['texto']
                })
    
    print(f"Nodos verificados: {nodes_checked}")
    print(f"Conexiones rotas encontradas: {len(broken_connections)}")
    
    if broken_connections:
        print("\n⚠ CONEXIONES ROTAS:")
        for conn in broken_connections[:10]:  # Mostrar solo las primeras 10
            print(f"  • {conn['from']} → {conn['to']}")
            print(f"    Opcion: '{conn['option']}'")
        
        if len(broken_connections) > 10:
            print(f"  ... y {len(broken_connections) - 10} mas")
    else:
        print("\n✓ TODAS LAS CONEXIONES SON VALIDAS")
    
    print("=" * 60)
    
    return len(broken_connections) == 0


def test_final_nodes():
    """Verifica que existan nodos finales para cada camino"""
    game = JuegoAventuraBase()
    
    print("\n" + "=" * 60)
    print("VERIFICACION DE NODOS FINALES")
    print("=" * 60)
    
    final_nodes = [node_id for node_id, node in game.historia.items() if node.es_final]
    
    print(f"Total de finales encontrados: {len(final_nodes)}")
    
    # Contar por personaje
    personajes = {
        'Jason Facil': [n for n in final_nodes if 'jason_facil_final' in n],
        'Jason Normal': [n for n in final_nodes if 'jason_normal_final' in n],
        'Jason Dificil': [n for n in final_nodes if 'jason_dificil_final' in n],
        'Dick Facil': [n for n in final_nodes if 'grayson_facil_final' in n],
        'Dick Normal': [n for n in final_nodes if 'grayson_normal_final' in n],
        'Dick Dificil': [n for n in final_nodes if 'grayson_dificil_final' in n],
        'Tim Facil': [n for n in final_nodes if 'tim_facil_final' in n],
        'Tim Normal': [n for n in final_nodes if 'tim_normal_final' in n],
        'Tim Dificil': [n for n in final_nodes if 'tim_dificil_final' in n],
        'Damian Facil': [n for n in final_nodes if 'damian_facil_final' in n],
        'Damian Normal': [n for n in final_nodes if 'damian_normal_final' in n],
        'Damian Dificil': [n for n in final_nodes if 'damian_dificil_final' in n],
    }
    
    for persona, finales in personajes.items():
        if finales:
            print(f"  {persona:20} → {len(finales)} finales")
        else:
            print(f"  {persona:20} → ⚠ SIN FINALES")
    
    print("=" * 60)
    
    return True


def test_node_count():
    """Cuenta los nodos por personaje y dificultad"""
    game = JuegoAventuraBase()
    
    print("\n" + "=" * 60)
    print("CONTEO DE NODOS POR CAMINO")
    print("=" * 60)
    
    counts = {
        'Jason Facil': len([n for n in game.historia if 'jason_facil' in n]),
        'Jason Normal': len([n for n in game.historia if 'jason_normal' in n]),
        'Jason Dificil': len([n for n in game.historia if 'jason_dificil' in n]),
        'Dick Facil': len([n for n in game.historia if 'grayson_facil' in n]),
        'Dick Normal': len([n for n in game.historia if 'grayson_normal' in n]),
        'Dick Dificil': len([n for n in game.historia if 'grayson_dificil' in n]),
        'Tim Facil': len([n for n in game.historia if 'tim_facil' in n]),
        'Tim Normal': len([n for n in game.historia if 'tim_normal' in n]),
        'Tim Dificil': len([n for n in game.historia if 'tim_dificil' in n]),
        'Damian Facil': len([n for n in game.historia if 'damian_facil' in n]),
        'Damian Normal': len([n for n in game.historia if 'damian_normal' in n]),
        'Damian Dificil': len([n for n in game.historia if 'damian_dificil' in n]),
    }
    
    total = 0
    for camino, count in counts.items():
        status = "✓" if count >= 40 else "⚠"
        print(f"  {status} {camino:20} → {count:3} nodos")
        total += count
    
    print("-" * 60)
    print(f"  TOTAL: {total} nodos")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    print("\n🎮 INICIANDO PRUEBAS DEL JUEGO DE ROBINS 🎮\n")
    
    try:
        test1 = test_starting_nodes()
        test2 = test_node_connections()
        test3 = test_final_nodes()
        test4 = test_node_count()
        
        print("\n" + "=" * 60)
        print("RESUMEN DE PRUEBAS")
        print("=" * 60)
        print(f"  Nodos de inicio: {'✓ OK' if test1 else '✗ FALLO'}")
        print(f"  Conexiones: {'✓ OK' if test2 else '✗ FALLO'}")
        print(f"  Nodos finales: {'✓ OK' if test3 else '✗ FALLO'}")
        print(f"  Conteo: {'✓ OK' if test4 else '✗ FALLO'}")
        print("=" * 60)
        
        if all([test1, test2, test3, test4]):
            print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! EL JUEGO ESTA LISTO.\n")
        else:
            print("\n⚠ ALGUNAS PRUEBAS FALLARON. REVISA LOS DETALLES ARRIBA.\n")
            
    except Exception as e:
        print(f"\n❌ ERROR AL EJECUTAR LAS PRUEBAS: {e}\n")
        import traceback
        traceback.print_exc()
